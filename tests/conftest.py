from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mex.drop.main import app
from mex.drop.settings import DropSettings

pytest_plugins = ("mex.common.testing.plugin",)


@pytest.fixture(autouse=True)
def settings(tmp_path: Path) -> DropSettings:
    """Load the settings for this pytest session."""
    settings = DropSettings.get()
    settings.drop_root_path = str(tmp_path)
    return settings


@pytest.fixture
def client() -> TestClient:
    """Return a fastAPI test client initialized with our app."""
    return TestClient(app)
