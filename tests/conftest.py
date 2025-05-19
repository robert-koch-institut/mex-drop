from collections.abc import Callable
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mex.drop.settings import DropSettings
from mex.drop.state import State, User
from mex.drop.types import APIKey
from mex.mex import app

pytest_plugins = ("mex.common.testing.plugin",)
TESTDATA_DIR = Path(__file__).parent / "test_files"


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
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    is_integration_test: bool,  # noqa: FBT001
) -> None:
    """Set the `MEX_WORK_DIR` environment variable to a temp path for all tests."""
    if not is_integration_test:
        monkeypatch.setenv("MEX_WORK_DIR", str(tmp_path))


@pytest.fixture(autouse=True)
def settings(is_integration_test: bool) -> DropSettings:  # noqa: FBT001
    """Load the settings for this pytest session."""
    settings = DropSettings.get()
    if not is_integration_test:
        settings.drop_api_key_database = TEST_USER_DATABASE
    return settings


@pytest.fixture
def client() -> TestClient:
    """Return a fastAPI test client initialized with our app."""
    return TestClient(app.api)


@pytest.fixture
def get_test_key() -> Callable[[str], str]:
    def _get_test_key(system: str) -> str:
        settings = DropSettings.get()
        secret_key = [
            key
            for key, x_sys in settings.drop_api_key_database.items()
            if system in x_sys
        ]
        if not secret_key:
            msg = f"Test key not found in database: {settings.drop_api_key_database}"
            raise ValueError(msg)
        return secret_key[0].get_secret_value()

    return _get_test_key


@pytest.fixture
def clean_test_directory() -> Callable[[], Path]:
    def _clean_test_directory() -> Path:
        """Fixture to clean a directory before a test."""
        settings = DropSettings.get()
        test_dir = Path(settings.drop_directory, "test")

        test_dir.mkdir(parents=True, exist_ok=True)

        for item in test_dir.iterdir():
            if item.is_file():
                item.unlink()

        return test_dir

    return _clean_test_directory


@pytest.fixture
def app_state(get_test_key: Callable[[str], str]) -> State:
    """Fixture to set up a global state with a mock user."""
    return State(user=User(x_system="test_system", api_key=get_test_key("test_system")))
