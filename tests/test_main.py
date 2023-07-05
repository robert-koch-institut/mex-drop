import pytest
from fastapi.testclient import TestClient


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
