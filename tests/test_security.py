import pytest

from mex.drop.security import is_authorized
from mex.drop.types import XSystem


@pytest.mark.parametrize(
    ("x_system", "authorized_x_systems", "expected"),
    [
        (
            XSystem("foo"),
            [
                XSystem("foo"),
            ],
            True,
        ),
        (XSystem("bar"), [XSystem("foo"), XSystem("admin")], True),
        (
            XSystem("foo"),
            [
                XSystem("bar"),
            ],
            False,
        ),
    ],
)
def test_is_authorized(
    x_system: XSystem,
    authorized_x_systems: list[XSystem],
    expected: bool,  # noqa: FBT001
) -> None:
    assert is_authorized(x_system, authorized_x_systems) is expected
