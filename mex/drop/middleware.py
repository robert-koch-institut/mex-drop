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


def get_frontend_csp(api_url: str) -> str:
    """Get the CSP for the frontend that talks to the api at the given url.

    Reflex runs inline scripts, evaluates scripts sent by the backend (for example
    `rx.call_script`) and injects styles at runtime, hence the 'unsafe-*' sources.
    """
    api = urlsplit(api_url)
    http_origin = f"{api.scheme}://{api.netloc}"
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


def add_security_headers(app: FastAPI, csp: str, cache_control: str) -> None:
    """Set security headers on every http response of the given app."""

    @app.middleware("http")
    async def set_security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers.update(SECURITY_HEADERS)
        response.headers["Content-Security-Policy"] = (
            DOCS_CSP if request.url.path.endswith(DOCS_PATHS) else csp
        )
        response.headers.setdefault("Cache-Control", cache_control)
        return response
