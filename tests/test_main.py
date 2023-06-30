from fastapi.testclient import TestClient


def test_read_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200, response.text
    assert response.json() == {"Hello": "World"}


def test_post_data(client: TestClient) -> None:
    x_system = "foo"
    entity = "bar"
    expected_response_code = 200
    response = client.post(f"/{x_system}/{entity}", json={"asd": "def"})
    assert response.status_code == expected_response_code, response.text
