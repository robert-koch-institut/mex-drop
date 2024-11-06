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
def isolate_work_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, is_integration_test: bool
) -> None:
    """Set the `MEX_WORK_DIR` environment variable to a temp path for all tests."""
    if not is_integration_test:
        monkeypatch.setenv("MEX_WORK_DIR", str(tmp_path))


@pytest.fixture(autouse=True)
def settings(is_integration_test: bool) -> DropSettings:
    """Load the settings for this pytest session."""
    settings = DropSettings.get()
    if not is_integration_test:
        settings.drop_api_key_database = TEST_USER_DATABASE
    return settings


@pytest.fixture
def client() -> TestClient:
    """Return a fastAPI test client initialized with our app."""
    return TestClient(app.api)
