from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.datastructures import Headers
from starlette.exceptions import HTTPException

if TYPE_CHECKING:  # pragma: no cover
    from starlette.types import Scope

# The frontend is pre-built with this api url (see Dockerfile) and the real
# api url is swapped in when serving the `reflex-env-*.js` chunk.
API_URL_PLACEHOLDER = "http://mex-api-url-placeholder"
ROOT_BUILD_NAME = "root"


class SPAStaticFiles(StaticFiles):
    """Static files that fall back to a given html page for SPA navigation."""

    def __init__(self, *, directory: Path, fallback: str) -> None:
        """Serve files from `directory` and fall back to `fallback` for html."""
        super().__init__(directory=directory, html=True)
        self.fallback = fallback

    async def get_response(self, path: str, scope: Scope) -> Response:
        """Try to serve the file at `path`, or fall back for SPA navigation."""
        try:
            response = await super().get_response(path, scope)
        except HTTPException as error:
            if error.status_code != status.HTTP_404_NOT_FOUND:
                raise
            response = Response(status_code=status.HTTP_404_NOT_FOUND)
        # Only fall back for navigation requests (browsers asking for html),
        # asset requests should get a real 404.
        if response.status_code == status.HTTP_404_NOT_FOUND and "text/html" in (
            Headers(scope=scope).get("accept", "")
        ):
            return await super().get_response(self.fallback, scope)
        return response


def get_build_directory(frontend_directory: Path, frontend_path: str) -> Path:
    """Get the directory of the pre-built frontend for the given frontend path."""
    build_name = frontend_path.strip("/") or ROOT_BUILD_NAME
    build_directory = frontend_directory / build_name
    if not build_directory.is_dir():
        available = sorted(p.name for p in frontend_directory.glob("*") if p.is_dir())
        msg = (
            f"No pre-built frontend for frontend path '{frontend_path}' found in "
            f"'{frontend_directory}', available builds: {available}"
        )
        raise SystemExit(msg)
    return build_directory


def render_env_chunk(content: str, api_url: str) -> str:
    """Replace the api url placeholder in the reflex env chunk."""
    api_url = api_url.rstrip("/")
    ws_placeholder = API_URL_PLACEHOLDER.replace("http", "ws", 1)
    ws_url = api_url.replace("http", "ws", 1)
    return content.replace(ws_placeholder, ws_url).replace(API_URL_PLACEHOLDER, api_url)


def _static_response(content: str) -> Callable[[], Response]:
    """Return an endpoint that always serves the given javascript content."""
    return lambda: Response(content, media_type="text/javascript")


def create_frontend_app(
    build_directory: Path, frontend_path: str, api_url: str
) -> FastAPI:
    """Create an app serving the pre-built frontend with the given api url."""
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    for env_chunk in build_directory.glob("**/assets/reflex-env-*.js"):
        content = render_env_chunk(env_chunk.read_text(encoding="utf-8"), api_url)
        app.get(f"/{env_chunk.relative_to(build_directory).as_posix()}")(
            _static_response(content)
        )
    prefix = frontend_path.strip("/")
    app.mount(
        "/",
        SPAStaticFiles(
            directory=build_directory,
            fallback=f"{prefix}/404.html" if prefix else "404.html",
        ),
    )
    return app
