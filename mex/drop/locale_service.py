import re
from collections.abc import Iterable
from gettext import GNUTranslations
from importlib.resources import files
from io import BytesIO
from pathlib import Path
from typing import Self, cast

import polib
from babel import Locale as BabelLocale
from pydantic import BaseModel

from mex.common.context import SingleSingletonStore

LOCALE_SERVICE_STORE = SingleSingletonStore["LocaleService"]()

# ISO 639-2/T codes used as short language labels in the UI
ISO_639_2_CODES = {"de": "deu", "en": "eng"}


class MExLocale(BaseModel):
    """Represents a locale with id and label."""

    id: str
    label: str
    language: str
    code: str

    def values(self) -> Iterable[str]:
        """Expose locale values to avoid reflex bug."""
        return self.model_dump().values()  # sigh, don't ask


class LocaleService:
    """A service singleton to control the current locale used by the app."""

    @classmethod
    def get(cls) -> Self:
        """Get singleton instance of the LocaleService.

        Returns:
            The LocaleService singleton.
        """
        return cast("Self", LOCALE_SERVICE_STORE.load(cls))

    _drop_locale_path = cast("Path", (files("mex.drop") / "i18n"))
    _available_locales: dict[str, MExLocale] = {}
    _translations: dict[str, GNUTranslations] = {}

    def __init__(self) -> None:
        """Initialize with all available locales in `_drop_locale_path`."""
        for po_file in sorted(self._drop_locale_path.glob("*.po")):
            locale = po_file.name.removesuffix(".po")
            language = re.split("[-_]", locale)[0]
            label = BabelLocale(language).get_language_name()
            code = ISO_639_2_CODES.get(language, language).upper()
            self._available_locales[locale] = MExLocale(
                id=locale, label=label, language=language, code=code
            )

    def _ensure_translation(self, locale_id: str) -> GNUTranslations:
        if locale_id not in self._available_locales:
            valid = ", ".join(locale.id for locale in self.get_available_locales())
            error_msg = (
                f"Given 'locale_id' ({locale_id}) is not valid. "
                f"Valid values are: {valid}"
            )
            raise ValueError(error_msg)

        if locale_id not in self._translations:
            drop_po = polib.pofile(self._drop_locale_path / f"{locale_id}.po")
            self._translations[locale_id] = GNUTranslations(
                BytesIO(drop_po.to_binary())
            )
        return self._translations[locale_id]

    def get_available_locales(self) -> list[MExLocale]:
        """Get all available locales.

        Returns:
            All available locales.
        """
        return list(self._available_locales.values())

    def get_ui_label(self, locale_id: str, msg_id: str) -> str:
        """Get the text for a given locale_id and the msg_id.

        Args:
            locale_id: The locale to use.
            msg_id: The message id of the message to get the text for.

        Returns:
            The message of the msg_id for the given locale_id.
        """
        translation = self._ensure_translation(locale_id)
        return translation.gettext(msg_id)
