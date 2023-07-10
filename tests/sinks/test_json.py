import json
from pathlib import Path

import pytest

from mex.drop.sinks.json import json_sink


@pytest.mark.asyncio
async def test_json(tmp_path: Path) -> None:
    expected_file = tmp_path / "out.json"
    expected_content = {
        "asd": "def",
        "foo": 1,
        "bar": 1.2,
        "list": [1, 2, 3],
        "dict": {"a": "b"},
    }
    await json_sink(expected_content, expected_file)
    assert expected_file.is_file()
    with expected_file.open(encoding="utf-8") as handle:
        content = json.load(handle)
    assert content == expected_content
