from fastapi.testclient import TestClient


def test_read_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200, response.text
    assert response.json() == {"Hello": "World"}
