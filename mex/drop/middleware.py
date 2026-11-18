from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from starlette import status
from starlette.datastructures import Headers
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from mex.drop.settings import DropSettings

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fastapi import FastAPI, Request, Response
    from starlette.types import ASGIApp, Message, Receive, Scope, Send

SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "DENY",
}
# the api only serves json, so nothing may be loaded or framed
API_CSP = "default-src 'none'; frame-ancestors 'none'"
# the swagger ui loads its js and css from jsdelivr and runs one inline script
DOCS_CSP = (
    "default-src 'none'; "
    "script-src https://cdn.jsdelivr.net 'unsafe-inline'; "
    "style-src https://cdn.jsdelivr.net; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'"
)
DOCS_PATHS = ("/docs", "/docs/oauth2-redirect")
# api hostnames that reflex replaces with the hostname the frontend is served from
SAME_DOMAIN_HOSTNAMES = ("localhost", "0.0.0.0", "::", "0:0:0:0:0:0:0:0")  # noqa: S104


def get_api_origin(api_url: str, frontend_url: str) -> str:
    """Get the origin the frontend at the given url uses to reach the api.

    Mirrors `getBackendURL` in reflex's `state.js`: when the api url names one of
    `SAME_DOMAIN_HOSTNAMES`, the browser swaps in the hostname of the frontend, and
    on https it also switches to https and drops the port.
    """
    api = urlsplit(api_url)
    frontend = urlsplit(frontend_url)
    if api.hostname not in SAME_DOMAIN_HOSTNAMES or not frontend.hostname:
        return f"{api.scheme}://{api.netloc}"
    host = f"[{frontend.hostname}]" if ":" in frontend.hostname else frontend.hostname
    if frontend.scheme == "https":
        return f"https://{host}"
    port = f":{api.port}" if api.port else ""
    return f"{api.scheme}://{host}{port}"


def get_frontend_csp(api_url: str, frontend_url: str) -> str:
    """Get the CSP for the frontend at `frontend_url` that talks to `api_url`.

    Reflex runs inline scripts, evaluates scripts sent by the backend (for example
    `rx.call_script`) and injects styles at runtime, hence the 'unsafe-*' sources.
    """
    http_origin = get_api_origin(api_url, frontend_url)
    ws_origin = http_origin.replace("http", "ws", 1)
    return (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' data:; "
        f"connect-src 'self' {http_origin} {ws_origin}; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "object-src 'none'"
    )


def add_security_headers(
    app: FastAPI, csp: str | Callable[[Request], str], cache_control: str
) -> None:
    """Set security headers on every http response of the given app.

    The CSP is either fixed or built for each request by the given callable.
    """

    @app.middleware("http")
    async def set_security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers.update(SECURITY_HEADERS)
        if request.url.path.endswith(DOCS_PATHS):
            response.headers["Content-Security-Policy"] = DOCS_CSP
        else:
            response.headers["Content-Security-Policy"] = (
                csp(request) if callable(csp) else csp
            )
        response.headers.setdefault("Cache-Control", cache_control)
        return response


class RequestTooLargeError(HTTPException):
    """Raised when a request body exceeds the configured upload size.

    Subclasses `HTTPException`, because fastapi turns any other error raised while
    reading the body into a 400 response.
    """

    def __init__(self, max_size: int) -> None:
        """Create a 413 error for the given maximum size."""
        super().__init__(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Request body exceeds the maximum size of {max_size} bytes.",
        )


class RequestSizeLimitMiddleware:
    """Reject http requests whose body exceeds `drop_max_upload_size`.

    Requests announcing a too large `Content-Length` are rejected right away,
    others are counted while the body is being read, so chunked uploads are
    capped too and never fully buffered.
    """

    def __init__(self, app: ASGIApp) -> None:
        """Wrap the given asgi app."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Handle a request, responding with 413 if its body is too large."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        max_size = DropSettings.get().drop_max_upload_size
        content_length = Headers(scope=scope).get("content-length", "")
        if content_length.isdigit() and int(content_length) > max_size:
            await self._reject(RequestTooLargeError(max_size), scope, receive, send)
            return

        received = 0
        response_started = False

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > max_size:
                    raise RequestTooLargeError(max_size)
            return message

        async def tracking_send(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, tracking_send)
        except RequestTooLargeError as error:
            # fallback for apps that do not turn the HTTPException into a response
            if response_started:
                raise
            await self._reject(error, scope, receive, send)

    @staticmethod
    async def _reject(
        error: RequestTooLargeError, scope: Scope, receive: Receive, send: Send
    ) -> None:
        response = JSONResponse({"detail": error.detail}, error.status_code)
        await response(scope, receive, send)
