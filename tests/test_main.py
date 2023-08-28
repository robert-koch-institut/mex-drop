from pathlib import Path
from unittest.mock import AsyncMock, call

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

import mex
from mex.drop.settings import DropSettings
from mex.drop.types import EntityType, XSystem


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


def test_show_form(client: TestClient) -> None:
    response = client.get(
        "/v0/test_system/test_type",
    )

    assert response.status_code == 200, response.text
    assert "<title>mex-drop</title>" in response.text


def test_health_check(client: TestClient) -> None:
    response = client.get("/_system/check")
    assert response.status_code == 200, response.text
    assert response.json() == {"status": "ok"}
