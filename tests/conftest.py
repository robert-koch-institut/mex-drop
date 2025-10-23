from collections.abc import Callable
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AnyExtractedModel,
    ExtractedActivity,
    ExtractedContactPoint,
    ExtractedOrganizationalUnit,
    ExtractedPrimarySource,
    ExtractedResource,
)
from mex.common.types import (
    AccessRestriction,
    Link,
    Text,
    TextLanguage,
    Theme,
    YearMonthDay,
)
from mex.drop.settings import DropSettings
from mex.drop.state import State, User
from mex.drop.types import APIKey, UserDatabase
from mex.mex import app

pytest_plugins = ("mex.common.testing.plugin",)
TESTDATA_DIR = Path(__file__).parent / "test_files"


TEST_USER_DATABASE = UserDatabase(
    {
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
)


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


@pytest.fixture
def dummy_data() -> list[AnyExtractedModel]:
    """Create a set of interlinked dummy data."""
    primary_source_1 = ExtractedPrimarySource(
        hadPrimarySource=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        identifierInPrimarySource="ps-1",
        title=[Text(value="Primary Source One", language=TextLanguage.EN)],
    )
    primary_source_2 = ExtractedPrimarySource(
        hadPrimarySource=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        identifierInPrimarySource="ps-2",
        version="Cool Version v2.13",
        title=[Text(value="Primary Source Two", language=TextLanguage.EN)],
    )
    contact_point_1 = ExtractedContactPoint(
        email=["info@contact-point.one"],
        hadPrimarySource=primary_source_1.stableTargetId,
        identifierInPrimarySource="cp-1",
    )
    contact_point_2 = ExtractedContactPoint(
        email=["help@contact-point.two"],
        hadPrimarySource=primary_source_1.stableTargetId,
        identifierInPrimarySource="cp-2",
    )
    organizational_unit_1 = ExtractedOrganizationalUnit(
        hadPrimarySource=primary_source_2.stableTargetId,
        identifierInPrimarySource="ou-1",
        name=[Text(value="Unit 1", language=TextLanguage.EN)],
        shortName=["OU1"],
    )
    activity_1 = ExtractedActivity(
        abstract=[
            Text(value="An active activity.", language=TextLanguage.EN),
            Text(value="Une activité active.", language=None),
        ],
        contact=[
            contact_point_1.stableTargetId,
            organizational_unit_1.stableTargetId,
        ],
        hadPrimarySource=primary_source_1.stableTargetId,
        identifierInPrimarySource="a-1",
        responsibleUnit=[organizational_unit_1.stableTargetId],
        shortName=["A1"],
        start=[YearMonthDay(1999, 12, 24)],
        end=[YearMonthDay(2023, 1, 1)],
        theme=[Theme["INFECTIOUS_DISEASES_AND_EPIDEMIOLOGY"]],
        title=[Text(value="Aktivität 1", language=TextLanguage.DE)],
        website=[
            Link(title="Activity Homepage", url="https://activity-1"),
            Link(url="https://activity-homepage-1"),
        ],
    )
    resource_1 = ExtractedResource(
        hadPrimarySource=primary_source_1.stableTargetId,
        identifierInPrimarySource="r-1",
        accessRestriction=AccessRestriction["OPEN"],
        contact=[contact_point_1.stableTargetId],
        theme=[Theme["BIOINFORMATICS_AND_SYSTEMS_BIOLOGY"]],
        title=[Text(value="Bioinformatics Resource 1", language=None)],
        unitInCharge=[organizational_unit_1.stableTargetId],
    )
    resource_2 = ExtractedResource(
        hadPrimarySource=primary_source_2.stableTargetId,
        identifierInPrimarySource="r-2",
        accessRestriction=AccessRestriction["OPEN"],
        contact=[contact_point_1.stableTargetId, contact_point_2.stableTargetId],
        theme=[Theme["PUBLIC_HEALTH"]],
        title=[
            Text(value="Some Resource with many titles 1", language=None),
            Text(value="Some Resource with many titles 2", language=TextLanguage.EN),
            Text(value="Eine Resource mit vielen Titeln 3", language=TextLanguage.DE),
            Text(value="Some Resource with many titles 4", language=None),
        ],
        unitInCharge=[organizational_unit_1.stableTargetId],
    )
    return [
        primary_source_1,
        primary_source_2,
        contact_point_1,
        contact_point_2,
        organizational_unit_1,
        activity_1,
        resource_1,
        resource_2,
    ]


@pytest.fixture(autouse=True)
def flush_graph_database(is_integration_test: bool) -> None:  # noqa: FBT001
    """Flush the graph database before every integration test."""
    if is_integration_test:
        connector = BackendApiConnector.get()
        # TODO(ND): use proper connector method when available (stopgap mx-1984)
        connector.request(method="DELETE", endpoint="/_system/graph")


@pytest.fixture
def load_dummy_data(
    dummy_data: list[AnyExtractedModel],
    flush_graph_database: None,  # noqa: ARG001
) -> None:
    """Ingest dummy data into the backend."""
    connector = BackendApiConnector.get()
    connector.ingest(dummy_data)
