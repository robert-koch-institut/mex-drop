from pathlib import Path
from unittest.mock import MagicMock, call

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

import mex
from mex.drop.settings import DropSettings


@pytest.mark.parametrize(
    "x_system, entity, expected_response_code",
    [
        ("test_system", "bar", 202),
        ("foo_system", "bar", 202),
        ("test_system", "invalid entity", 422),
        ("unauthorized_system", "bar", 401),
        ("invalid x_system", "bar", 422),
    ],
    ids=(
        "valid",
        "valid2",
        "invalid entity",
        "unauthorized x_system",
        "invalid x_system",
    ),
)
def test_post_data(
    client: TestClient,
    x_system: str,
    entity: str,
    expected_response_code: int,
    monkeypatch: MonkeyPatch,
    settings: DropSettings,
) -> None:
    mocked_sink = MagicMock()
    monkeypatch.setattr(mex.drop.main, "json_sink", mocked_sink)
    expected_content = {
        "asd": "def",
        "foo": 1,
        "bar": 1.2,
        "list": [1, 2, 3],
        "dict": {"a": "b"},
    }
    expected_file = Path(settings.drop_root_path, x_system, entity + ".json")
    response = client.post(f"/v0/{x_system}/{entity}", json=expected_content)
    assert response.status_code == expected_response_code, response.text
    if 200 <= response.status_code < 300:
        assert mocked_sink.call_args == call(expected_content, expected_file)
