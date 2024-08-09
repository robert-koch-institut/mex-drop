import json
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, call

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

import mex
from mex.drop.settings import DropSettings
from mex.drop.types import EntityType, XSystem


@pytest.fixture
def dropped_data(tmp_path: Path) -> dict[str, Any]:
    """Dictionary of api key, x-system name, entity type and content."""
    settings = DropSettings.get()
    settings.drop_directory = tmp_path
    data = {
        "content": {"foo": "bar"},
        "api_key": "api-test-key",
        "x_system": "test_system",
        "entity_type": "foo",
    }
    x_system_dir = tmp_path / data["x_system"]
    expected_file = x_system_dir / f"{data['entity_type']}.json"
    x_system_dir.mkdir(parents=True)
    with expected_file.open("w") as handle:
        json.dump(data["content"], handle)
    return data


@pytest.mark.parametrize(
    "api_key, x_system, entity_type, expected_response_code",
    [
        ("api-test-key", "test_system", "valid_entity_type", 202),
        ("api-test-key", "foo_system", "valid_entity_type", 202),
        ("api-test-key", "test_system", "invalid entity type", 422),
        ("api-test-key", "invalid x_system", "valid_entity_type", 422),
        (None, "test_system", "valid_entity_type", 401),
        ("invalid-key", "test_system", "valid_entity_type", 401),
        ("api-key-one", "foo_system", "valid_entity_type", 403),
    ],
    ids=(
        "valid",
        "valid2",
        "invalid entity type",
        "invalid x_system",
        "missing header",
        "invalid api_key",
        "unauthorized x_system",
    ),
)
def test_drop_data(
    client: TestClient,
    api_key: str | None,
    x_system: XSystem,
    entity_type: EntityType,
    expected_response_code: int,
    monkeypatch: MonkeyPatch,
    settings: DropSettings,
) -> None:
    mocked_sink = AsyncMock(return_value=None)
    monkeypatch.setattr(mex.drop.main, "json_sink", mocked_sink)
    expected_content = {
        "asd": "def",
        "foo": 1,
        "bar": 1.2,
        "list": [1, 2, 3],
        "dict": {"a": "b"},
    }
    expected_file = Path(settings.drop_directory, x_system, entity_type + ".json")
    response = client.post(
        f"/v0/{x_system}/{entity_type}",
        headers={"X-API-Key": api_key} if api_key else {},
        json=expected_content,
    )
    assert response.status_code == expected_response_code, response.text
    if 200 <= response.status_code < 300:
        assert mocked_sink.call_args == call(expected_content, expected_file)


@pytest.mark.parametrize(
    "api_key, x_system, expected_response_code, files",
    [
        (
            "api-test-key",
            "test_system",
            202,
            {"file1.txt": "file1 content", "file2.csv": "1,2,3"},
        ),
        ("api-test-key", "foo_system", 422, {}),
        ("api-test-key", "invalid x_system", 422, {"file1.txt": "file1 content"}),
        (None, "test_system", 401, {"file1.txt": "file1 content"}),
        ("invalid-key", "test_system", 401, {"file1.txt": "file1 content"}),
        ("api-key-one", "foo_system", 403, {"file1.txt": "file1 content"}),
    ],
    ids=(
        "valid",
        "missing upload",
        "invalid x_system",
        "missing header",
        "invalid api_key",
        "unauthorized x_system",
    ),
)
def test_drop_multiple_files(
    client: TestClient,
    api_key: str | None,
    x_system: XSystem,
    expected_response_code: int,
    files: dict[str, str],
    settings: DropSettings,
) -> None:
    files_data = [
        ("files", (name, BytesIO(content.encode()), "text/plain"))
        for name, content in files.items()
    ]
    response = client.post(
        f"/v0/{x_system}",
        headers={"X-API-Key": api_key} if api_key else {},
        files=files_data,
    )
    assert response.status_code == expected_response_code, response.text
    if 200 <= response.status_code < 300 and files:
        for filename, content in files.items():
            expected_file1 = Path(settings.drop_directory, x_system, filename)
            assert expected_file1.read_text() == content


def test_download_data(client: TestClient, dropped_data: dict[str, Any]) -> None:
    client.headers.update({"X-API-Key": dropped_data["api_key"]})
    response = client.get(
        f"/v0/{dropped_data['x_system']}/{dropped_data['entity_type']}",
    )
    assert response.status_code == 200, response
    assert response.json() == dropped_data["content"]

    response = client.get(
        f"/v0/{dropped_data['x_system']}/entity_that_does_not_exist",
    )
    assert response.status_code == 404, response


def test_list_x_systems(client: TestClient, dropped_data: dict[str, Any]) -> None:
    response = client.get("/v0/", headers={"X-API-Key": "i-do-what-i-want"})
    assert response.status_code == 200, response.text
    assert response.json() == {"x-systems": [f"{dropped_data['x_system']}"]}


def test_list_entity_types(client: TestClient, dropped_data: dict[str, Any]) -> None:
    client.headers.update({"X-API-Key": dropped_data["api_key"]})
    response = client.get(
        f"/v0/{dropped_data['x_system']}",
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"entity-types": [f"{dropped_data['entity_type']}"]}

    response = client.get(
        "/v0/x_system_that_does_not_exist",
    )
    assert response.status_code == 404, response.text


def test_health_check(client: TestClient) -> None:
    response = client.get("/_system/check")
    assert response.status_code == 200, response.text
    assert response.json() == {"status": "ok"}
