from typing import cast
from unittest.mock import patch

from reflex import State
from reflex.vars.base import ComputedVar

from mex.drop.label_var import label_var
from mex.drop.locale_service import LocaleService

translations = {
    "locale-1": {
        "test_id": "locale-1.test_id",
        "test_dependency_id": "locale-1.test_dependency_id.{0}",
    },
    "locale-2": {
        "test_id": "locale-2.test_id",
        "test_dependency_id": "locale-2.test_dependency_id.{0}",
    },
}


def _get_text_mock(locale: str, msg_id: str) -> str:
    return translations[locale][msg_id]


class DummyState(State):
    current_locale: str = "locale-1"
    some_var: int = 1

    @label_var(label_id="test_id")  # type: ignore[type-var]
    def label_string_value(self) -> None:
        pass

    @label_var(label_id="test_dependency_id", deps=["some_var"])  # type: ignore[type-var]
    def label_with_dependencies(self) -> list[int]:
        return [self.some_var]


@patch.object(LocaleService.get(), LocaleService.get_ui_label.__name__, _get_text_mock)
def test_label_var_initial_state() -> None:
    state = DummyState()

    assert state.label_string_value == "locale-1.test_id"
    assert state.label_with_dependencies == "locale-1.test_dependency_id.1"


@patch.object(LocaleService.get(), LocaleService.get_ui_label.__name__, _get_text_mock)
def test_label_var_locale_change() -> None:
    state = DummyState()
    assert state.label_string_value == "locale-1.test_id"
    assert state.label_with_dependencies == "locale-1.test_dependency_id.1"

    state.current_locale = "locale-2"

    assert state.label_string_value == "locale-2.test_id"
    assert state.label_with_dependencies == "locale-2.test_dependency_id.1"


@patch.object(LocaleService.get(), LocaleService.get_ui_label.__name__, _get_text_mock)
def test_label_var_dependency_update() -> None:
    state = DummyState()
    assert state.label_with_dependencies == "locale-1.test_dependency_id.1"

    state.some_var = 245
    assert state.label_with_dependencies == "locale-1.test_dependency_id.245"

    state.current_locale = "locale-2"
    assert state.label_with_dependencies == "locale-2.test_dependency_id.245"


def test_label_var_tracks_current_locale_as_dependency() -> None:
    label_string = cast("ComputedVar[str]", DummyState.label_string_value)
    assert None in label_string._static_deps
    assert "current_locale" in label_string._static_deps[None]

    label_string_deps = cast("ComputedVar[str]", DummyState.label_with_dependencies)
    assert None in label_string_deps._static_deps
    assert "current_locale" in label_string_deps._static_deps[None]
    assert "some_var" in label_string_deps._static_deps[None]
