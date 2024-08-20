from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mex.drop.settings import DropSettings
from mex.drop.types import APIKey
from mex.mex import app

pytest_plugins = ("mex.common.testing.plugin",)


TEST_USER_DATABASE = {
    APIKey("api-key-one"): ["test_system"],
    APIKey("john-doe"): ["test_system", "foo_system"],
    APIKey("api-test-key"): [
        "test_system",
        "foo_system",
        "x_system_that_does_not_exist",
    ],
    APIKey("alice"): ["foo_system"],
    APIKey("i-do-what-i-want"): ["admin"],
}


@pytest.fixture(autouse=True)
def settings(tmp_path: Path) -> DropSettings:
    """Load the settings for this pytest session."""
    settings = DropSettings.get()
    settings.drop_directory = str(tmp_path)
    settings.drop_api_key_database = TEST_USER_DATABASE
    return settings


@pytest.fixture
def client() -> TestClient:
    """Return a fastAPI test client initialized with our app."""
    return TestClient(app.api)
