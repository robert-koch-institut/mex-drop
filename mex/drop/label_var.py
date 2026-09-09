import datetime
from collections.abc import Callable, Iterable
from functools import wraps
from typing import TYPE_CHECKING, Any, overload

from reflex.utils import types
from reflex.vars.base import ComputedVar, Var, computed_var

from mex.drop.locale_service import LocaleService

if TYPE_CHECKING:
    from mex.drop.state import State


@overload
def label_var[StateT: "State", ReturnT](
    fget: None = None,
    label_id: str = "",
    initial_value: Any | types.Unset = types.Unset(),  # noqa: ANN401, B008
    cache: bool = True,  # noqa: FBT001, FBT002
    deps: list[str | Var[str]] | None = None,
    interval: datetime.timedelta | int | None = None,
    backend: bool | None = None,  # noqa: FBT001
    **kwargs: Any,  # noqa: ANN401
) -> Callable[[Callable[[StateT], ReturnT]], ComputedVar[str]]: ...


@overload
def label_var[StateT: "State", ReturnT](
    fget: Callable[[StateT], ReturnT],
    label_id: str,
    initial_value: ReturnT | types.Unset = types.Unset(),  # noqa: B008
    cache: bool = True,  # noqa: FBT001, FBT002
    deps: list[str | Var[str]] | None = None,
    interval: datetime.timedelta | int | None = None,
    backend: bool | None = None,  # noqa: FBT001
    **kwargs: Any,  # noqa: ANN401
) -> ComputedVar[str]: ...


def label_var[StateT: "State"](  # noqa: PLR0913, PLR0917
    fget: Callable[[StateT], Any] | None = None,  # noqa: ARG001
    label_id: str = "",
    initial_value: Any | types.Unset = types.Unset(),  # noqa: B008
    cache: bool = True,  # noqa: FBT001, FBT002
    deps: list[str | Var[str]] | None = None,
    interval: datetime.timedelta | int | None = None,
    backend: bool | None = None,  # noqa: FBT001
    **kwargs: Any,
) -> ComputedVar[str] | Callable[[Callable[[StateT], Any]], ComputedVar[str]]:
    """A decorator to translate the given label_id base on the current locale.

    Args:
        fget: The getter function.
        label_id: The msgid to search for in the currents locale .po file
        initial_value: The initial value of the computed var.
        cache: Whether to cache the computed value.
        deps: Explicit var dependencies to track.
        interval: Interval at which the computed var should be updated.
        backend: Whether the computed var is a backend var.
        **kwargs: additional attributes to set on the instance

    Returns:
        A ComputedVar instance containing the translated label_id.

    Raises:
        ValueError: If caching is disabled and an update interval is set.
        VarDependencyError: If user supplies dependencies without caching.
        ComputedVarSignatureError: If the getter function has more than one argument.
    """
    locale_service = LocaleService.get()

    def wrapper(fget: Callable[[StateT], Any]) -> ComputedVar[str]:
        @wraps(
            fget,
            assigned=(
                "__module__",
                "__name__",
                "__qualname__",
            ),
        )
        def inner(state: StateT) -> str:
            result = fget(state)
            label = locale_service.get_ui_label(state.current_locale, label_id)
            if result and isinstance(result, Iterable):
                label = label.format(*result)
            return label

        # we know current_locale is always a dependency if inner
        inner_deps = deps or []
        inner_deps.append("current_locale")

        # we never want auto_deps since we set current_locale as dep and there are no
        # other deps inside inner. Auto discover deps inside fget would be awesome but
        # i couldn't figure out how :(
        return computed_var(
            inner,
            initial_value=initial_value,
            cache=cache,
            deps=inner_deps,
            auto_deps=False,
            interval=interval,
            backend=backend,
            **kwargs,
        )

    return wrapper
