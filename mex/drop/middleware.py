from typing import TYPE_CHECKING
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fastapi import FastAPI, Request, Response

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
