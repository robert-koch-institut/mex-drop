import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mex.drop.settings import DropSettings


def test_read_root(client: TestClient) -> None:
    response = client.get("/api/v0/")
    assert response.status_code == 200, response.text
    assert response.json() == {"Hello": "World"}


@pytest.mark.parametrize(
    "x_system, entity, expected_response_code",
    [
        ("foo", "bar", 201),
        ("invalid x_system", "bar", 422),
        ("foo", "invalid entity", 422),
    ],
    ids=(
        "valid",
        "invalid x_system",
        "invalid entity",
    ),
)
def test_post_data(
    client: TestClient, x_system: str, entity: str, expected_response_code: int
) -> None:
    response = client.post(f"/api/v0/{x_system}/{entity}", json={"asd": "def"})
    assert response.status_code == expected_response_code, response.text


def test_post_data_is_written_to_file(
    client: TestClient, settings: DropSettings
) -> None:
    relative_path = "wasd/def"
    expected_file = Path(settings.drop_root_path, relative_path + ".json")
    expected_content = {
        "asd": "def",
        "foo": 1,
        "bar": 1.2,
        "list": [1, 2, 3],
        "dict": {"a": "b"},
    }
    response = client.post("/api/v0/" + relative_path, json=expected_content)
    assert response.status_code == 201
    assert expected_file.is_file()
    with expected_file.open(encoding="utf-8") as handle:
        content = json.load(handle)
    assert content == expected_content
