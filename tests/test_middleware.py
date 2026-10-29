import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mex.drop.api.main import api
from mex.drop.middleware import (
    API_CSP,
    DOCS_CSP,
    SECURITY_HEADERS,
    add_security_headers,
    get_frontend_csp,
)


@pytest.mark.parametrize(
    ("api_url", "expected"),
    [
        (
            "http://localhost:8021",
            "connect-src 'self' http://localhost:8021 ws://localhost:8021;",
        ),
        (
            "https://dev.example.org/drop-api/",
            "connect-src 'self' https://dev.example.org wss://dev.example.org;",
        ),
    ],
    ids=["http", "https-with-path"],
)
def test_get_frontend_csp(api_url: str, expected: str) -> None:
    assert expected in get_frontend_csp(api_url)


@pytest.mark.parametrize(
    ("path", "expected_csp"),
    [("/", API_CSP), ("/docs", DOCS_CSP)],
    ids=["app", "docs"],
)
def test_add_security_headers(path: str, expected_csp: str) -> None:
    app = FastAPI()
    app.get("/")(dict)
    add_security_headers(app, API_CSP, "no-store")

    with TestClient(app) as client:
        response = client.get(path)

    assert response.headers["Content-Security-Policy"] == expected_csp
    assert response.headers["Cache-Control"] == "no-store"
    for name, value in SECURITY_HEADERS.items():
        assert response.headers[name] == value


def test_redoc_is_disabled() -> None:
    assert api.redoc_url is None
