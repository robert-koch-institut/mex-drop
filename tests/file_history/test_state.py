from unittest.mock import MagicMock, patch

from mex.drop.file_history.state import ListState
from mex.drop.state import User


def test_get_uploaded_files(get_test_key) -> None:
    list_state = ListState(
        user=User(x_system="test_system", api_key=get_test_key("test_system"))
    )
    with (
        patch("pathlib.Path.is_dir", return_value=True),
        patch(
            "pathlib.Path.glob",
            return_value=[
                MagicMock(
                    is_file=MagicMock(return_value=True),
                    stat=MagicMock(
                        name="file1.json", st_ctime=1609459200, st_mtime=1609459200
                    ),
                    name="file1.json",
                ),
                MagicMock(
                    is_file=MagicMock(return_value=True),
                    stat=MagicMock(
                        name="file2.csv", st_ctime=1609459200, st_mtime=1609459200
                    ),
                ),
            ],
        ),
        patch("mex.drop.state.State.check_login", return_value=None),
    ):
        list_state.get_uploaded_files()
        assert len(list_state.file_list) == 2
        assert list_state.file_list[0]["name"] == "file1.json"
        assert list_state.file_list[1]["name"] == "file2.csv"
