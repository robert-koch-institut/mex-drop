import pytest
from fastapi.testclient import TestClient

from mex.drop.main import app
from mex.drop.settings import DropSettings

pytest_plugins = ("mex.common.testing.plugin",)


@pytest.fixture(autouse=True)
def settings() -> DropSettings:
    """Load the settings for this pytest session."""
    return DropSettings.get()


@pytest.fixture
def client() -> TestClient:
    """Return a fastAPI test client initialized with our app."""
    return TestClient(app)
