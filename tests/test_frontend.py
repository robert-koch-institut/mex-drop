from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mex.drop.frontend import (
    API_URL_PLACEHOLDER,
    create_frontend_app,
    get_build_directory,
    render_env_chunk,
)

ENV_CHUNK = (
    f"var e={{PING:`{API_URL_PLACEHOLDER}/ping`,"
    f"EVENT:`ws://mex-api-url-placeholder/_event`,"
    f"UPLOAD:`{API_URL_PLACEHOLDER}/_upload`}};export{{e as t}};"
)


def write_build(directory: Path, prefix: str = "") -> None:
    build = directory / prefix
    (build / "assets").mkdir(parents=True)
    (build / "index.html").write_text("index")
    (build / "404.html").write_text("fallback")
    (build / "assets" / "reflex-env-abc123.js").write_text(ENV_CHUNK)
    (build / "assets" / "main-def456.js").write_text("main")


@pytest.mark.parametrize(
    ("api_url", "expected"),
    [
        (
            "http://localhost:8021",
            (
                "var e={PING:`http://localhost:8021/ping`,"
                "EVENT:`ws://localhost:8021/_event`,"
                "UPLOAD:`http://localhost:8021/_upload`};export{e as t};"
            ),
        ),
        (
            "https://dev.example.org/drop-api/",
            (
                "var e={PING:`https://dev.example.org/drop-api/ping`,"
                "EVENT:`wss://dev.example.org/drop-api/_event`,"
                "UPLOAD:`https://dev.example.org/drop-api/_upload`};export{e as t};"
            ),
        ),
    ],
    ids=["http", "https-with-path"],
)
def test_render_env_chunk(api_url: str, expected: str) -> None:
    assert render_env_chunk(ENV_CHUNK, api_url) == expected


def test_get_build_directory(tmp_path: Path) -> None:
    (tmp_path / "root").mkdir()
    (tmp_path / "drop").mkdir()

    assert get_build_directory(tmp_path, "") == tmp_path / "root"
    assert get_build_directory(tmp_path, "/") == tmp_path / "root"
    assert get_build_directory(tmp_path, "/drop") == tmp_path / "drop"
    assert get_build_directory(tmp_path, "drop/") == tmp_path / "drop"


def test_get_build_directory_missing(tmp_path: Path) -> None:
    (tmp_path / "root").mkdir()

    with pytest.raises(SystemExit, match=r"available builds: \['root'\]"):
        get_build_directory(tmp_path, "/nope")


@pytest.mark.parametrize("prefix", ["", "drop"], ids=["root", "prefixed"])
def test_create_frontend_app(tmp_path: Path, prefix: str) -> None:
    write_build(tmp_path, prefix)
    app = create_frontend_app(tmp_path, f"/{prefix}", "https://api.example.org")
    client = TestClient(app)
    base = f"/{prefix}/" if prefix else "/"

    response = client.get(base)
    assert response.status_code == 200
    assert response.text == "index"

    response = client.get(f"{base}assets/reflex-env-abc123.js")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/javascript")
    assert "wss://api.example.org/_event" in response.text
    assert API_URL_PLACEHOLDER not in response.text

    response = client.get(f"{base}assets/main-def456.js")
    assert response.status_code == 200
    assert response.text == "main"

    response = client.get(f"{base}upload", headers={"accept": "text/html"})
    assert response.status_code == 200
    assert response.text == "fallback"

    response = client.get(f"{base}assets/missing.js")
    assert response.status_code == 404
