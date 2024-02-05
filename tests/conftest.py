from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mex.drop.main import app
from mex.drop.settings import DropSettings
from mex.drop.types import APIKey

pytest_plugins = ("mex.common.testing.plugin",)


TEST_USER_DATABASE = {
    APIKey("api-key-one"): ["test_system"],
    APIKey("john-doe"): ["test_system", "foo_system"],
    APIKey("api-test-key"): ["test_system", "foo_system"],
    APIKey("alice"): ["foo_system"],
    APIKey("i-do-what-i-want"): ["admin"],
}


@pytest.fixture(autouse=True)
def settings(tmp_path: Path) -> DropSettings:
    """Load the settings for this pytest session."""
    settings = DropSettings.get()
    settings.drop_directory = str(tmp_path)
    settings.drop_user_database = TEST_USER_DATABASE
    return settings


@pytest.fixture
def client() -> TestClient:
    """Return a fastAPI test client initialized with our app."""
    return TestClient(app)
