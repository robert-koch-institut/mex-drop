import json
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, call

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

import mex
from mex.drop.files_io import ALLOWED_CONTENT_TYPES
from mex.drop.settings import DropSettings
from mex.drop.types import EntityType, XSystem

TESTDATA_DIR = Path(__file__).parent / "test_files"


@pytest.fixture
def dropped_data(tmp_path: Path) -> dict[str, Any]:
    """Dictionary of api key, x-system name, entity type and content."""
    settings = DropSettings.get()
    settings.drop_directory = tmp_path
    data = {
        "content": {"foo": "bar"},
        "api_key": "api-test-key",
        "x_system": "test_system",
        "entity_type": "foo",
    }
    x_system_dir = tmp_path / data["x_system"]
    expected_file = x_system_dir / f"{data['entity_type']}.json"
    x_system_dir.mkdir(parents=True)
    with expected_file.open("w") as handle:
        json.dump(data["content"], handle)
    return data


@pytest.mark.parametrize(
    (
        "api_key",
        "x_system",
        "entity_type",
        "expected_response_code",
        "content_type",
        "expected_content",
    ),
    [
        (
            "api-test-key",
            "test_system",
            "valid_entity_type",
            200,
            "application/json",
            {
                "asd": "def",
                "foo": 1,
                "bar": 1.2,
                "list": [1, 2, 3],
                "dict": {"a": "b"},
            },
        ),
        (
            "api-test-key",
            "foo_system",
            "valid_entity_type",
            200,
            "text/csv",
            "asd,foo,bar,list,dict.a\ndef,1,1.2,\"[1, 2, 3]\",\"{'a': 'b'}\"\n",
        ),
        (
            "api-test-key",
            "test_system",
            "valid_entity_type",
            200,
            "application/xml",
            (TESTDATA_DIR / "test.xml").read_text(),
        ),
        (
            "api-test-key",
            "test_system",
            "valid_entity_type",
            200,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            (TESTDATA_DIR / "test.xlsx").read_bytes(),
        ),
        (
            "api-test-key",
            "test_system",
            "valid_entity_type",
            400,
            "application/pdf",
            "foo",
        ),
        (
            "api-test-key",
            "test_system",
            "invalid entity type",
            422,
            "application/json",
            {
                "asd": "def",
                "foo": 1,
                "bar": 1.2,
                "list": [1, 2, 3],
                "dict": {"a": "b"},
            },
        ),
        (
            "api-test-key",
            "invalid x_system",
            "valid_entity_type",
            422,
            "application/json",
            {
                "asd": "def",
                "foo": 1,
                "bar": 1.2,
                "list": [1, 2, 3],
                "dict": {"a": "b"},
            },
        ),
        (
            None,
            "test_system",
            "valid_entity_type",
            401,
            "application/json",
            {
                "asd": "def",
                "foo": 1,
                "bar": 1.2,
                "list": [1, 2, 3],
                "dict": {"a": "b"},
            },
        ),
        (
            "invalid-key",
            "test_system",
            "valid_entity_type",
            401,
            "application/json",
            {
                "asd": "def",
                "foo": 1,
                "bar": 1.2,
                "list": [1, 2, 3],
                "dict": {"a": "b"},
            },
        ),
        (
            "api-key-one",
            "foo_system",
            "valid_entity_type",
            403,
            "application/json",
            {
                "asd": "def",
                "foo": 1,
                "bar": 1.2,
                "list": [1, 2, 3],
                "dict": {"a": "b"},
            },
        ),
    ],
    ids=(
        "valid",
        "valid csv",
        "valid xml",
        "valid xlsx",
        "invalid content type",
        "invalid entity type",
        "invalid x_system",
        "missing header",
        "invalid api_key",
        "unauthorized x_system",
    ),
)
def test_drop_data(
    client: TestClient,
    api_key: str | None,
    x_system: XSystem,
    entity_type: EntityType,
    expected_response_code: int,
    content_type: str,
    expected_content: Any,
    monkeypatch: MonkeyPatch,
    settings: DropSettings,
) -> None:
    mocked_sink = AsyncMock(return_value=None)
    monkeypatch.setattr(mex.drop.api, "json_sink", mocked_sink)

    if api_key:
        client.headers.update({"X-API-Key": api_key})
    client.headers.update({"Content-Type": content_type})
    kwargs = (
        {"json": expected_content}
        if content_type == "application/json"
        else {"content": expected_content}
    )
    response = client.post(f"/v0/{x_system}/{entity_type}", **kwargs)
    assert response.status_code == expected_response_code, response.text

    if 200 <= response.status_code < 300:
        base_path = Path(settings.drop_directory, x_system, entity_type)
        expected_file = base_path.with_suffix(ALLOWED_CONTENT_TYPES[content_type])

        if content_type == "application/json":
            assert mocked_sink.call_args == call(expected_content, expected_file)
        else:
            with open(expected_file, "rb") as f:
                saved_content = f.read()

            if (
                content_type == "text/csv"
                or content_type == "text/tab-separated-values"
            ):
                assert saved_content.decode("utf-8") == expected_content
            elif (
                content_type
                == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                or content_type == "application/vnd.ms-excel"
            ):
                original_df = pd.read_excel(BytesIO(expected_content), sheet_name=None)
                saved_df = pd.read_excel(BytesIO(saved_content), sheet_name=None)

                assert original_df.keys() == saved_df.keys()

                for sheet in original_df.keys():
                    pd.testing.assert_frame_equal(original_df[sheet], saved_df[sheet])


@pytest.mark.parametrize(
    ("api_key", "x_system", "expected_response_code", "files"),
    [
        (
            "api-test-key",
            "test_system",
            202,
            {
                "file1.json": ["file1 content", "application/json"],
                "file2.csv": ["1,2,3", "text/csv"],
            },
        ),
        (
            "api-test-key",
            "test_system",
            202,
            {"file1.xls": ["file1 content", "application/vnd.ms-excel"]},
        ),
        (
            "api-test-key",
            "test_system",
            422,
            {"file1.html": ["file1 content", "text/html"]},
        ),
        ("api-test-key", "foo_system", 422, {}),
        (
            "api-test-key",
            "invalid x_system",
            422,
            {"file1.json": ["file1 content", "application/json"]},
        ),
        (
            None,
            "test_system",
            401,
            {"file1.json": ["file1 content", "application/json"]},
        ),
        (
            "invalid-key",
            "test_system",
            401,
            {"file1.json": ["file1 content", "application/json"]},
        ),
        (
            "api-key-one",
            "foo_system",
            403,
            {"file1.json": ["file1 content", "application/json"]},
        ),
    ],
    ids=(
        "valid",
        "valid xls",
        "invalid file format",
        "missing upload",
        "invalid x_system",
        "missing header",
        "invalid api_key",
        "unauthorized x_system",
    ),
)
def test_drop_multiple_files(
    client: TestClient,
    api_key: str | None,
    x_system: XSystem,
    expected_response_code: int,
    files: dict[str, list[str]],
    settings: DropSettings,
) -> None:
    files_data = [
        ("files", (name, BytesIO(content.encode()), content_type))
        for name, (content, content_type) in files.items()
    ]
    response = client.post(
        f"/v0/{x_system}",
        headers={"X-API-Key": api_key} if api_key else {},
        files=files_data,
    )
    assert response.status_code == expected_response_code, response.text
    if 200 <= response.status_code < 300 and files:
        for filename, (content, _) in files.items():
            expected_file1 = Path(settings.drop_directory, x_system, filename)
            assert expected_file1.read_text() == content


def test_download_data(client: TestClient, dropped_data: dict[str, Any]) -> None:
    client.headers.update({"X-API-Key": dropped_data["api_key"]})
    response = client.get(
        f"/v0/{dropped_data['x_system']}/{dropped_data['entity_type']}",
    )
    assert response.status_code == 200, response
    assert response.json() == dropped_data["content"]

    response = client.get(
        f"/v0/{dropped_data['x_system']}/entity_that_does_not_exist",
    )
    assert response.status_code == 404, response


def test_list_x_systems(client: TestClient, dropped_data: dict[str, Any]) -> None:
    response = client.get("/v0/", headers={"X-API-Key": "i-do-what-i-want"})
    assert response.status_code == 200, response.text
    assert response.json() == {"x-systems": [f"{dropped_data['x_system']}"]}


def test_list_x_systems_forbidden(client: TestClient) -> None:
    response = client.get("/v0/", headers={"X-API-Key": "alice"})
    assert response.status_code == 403


def test_list_entity_types(client: TestClient, dropped_data: dict[str, Any]) -> None:
    client.headers.update({"X-API-Key": dropped_data["api_key"]})
    response = client.get(
        f"/v0/{dropped_data['x_system']}",
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"entity-types": [f"{dropped_data['entity_type']}"]}

    response = client.get(
        "/v0/x_system_that_does_not_exist",
    )
    assert response.status_code == 404, response.text


def test_list_entity_types_forbidden(client: TestClient) -> None:
    client.headers.update({"X-API-Key": "alice"})
    response = client.get("/v0/test_system")
    assert response.status_code == 403, response.text


def test_health_check(client: TestClient) -> None:
    response = client.get("/_system/check")
    assert response.status_code == 200, response.text
    assert response.json() == {"status": "ok"}
