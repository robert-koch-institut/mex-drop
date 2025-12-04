from mex.common.settings import SETTINGS_STORE
from mex.drop.settings import DropSettings


def load_settings() -> DropSettings:
    """Reset the settings store and fetch the drop settings."""
    SETTINGS_STORE.reset()
    return DropSettings.get()
