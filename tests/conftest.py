from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mex.drop.main import app
from mex.drop.models.user import User
from mex.drop.settings import DropSettings

pytest_plugins = ("mex.common.testing.plugin",)


TEST_USER_DATABASE = {
    "johndoe": {
        "username": "johndoe",
        "x_system": "test_system",
    },
    "alice": {
        "username": "alice",
        "x_system": "foo_system",
    },
}


@pytest.fixture(autouse=True)
def settings(tmp_path: Path) -> DropSettings:
    """Load the settings for this pytest session."""
    settings = DropSettings.get()
    settings.drop_root_path = str(tmp_path)
    settings.drop_user_database = {k: User(**v) for k, v in TEST_USER_DATABASE.items()}
    return settings


@pytest.fixture
def client() -> TestClient:
    """Return a fastAPI test client initialized with our app."""
    client = TestClient(app)
    client.headers = {"X-API-Key": "johndoe"}
    return client
