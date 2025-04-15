from typing import Annotated

from pydantic import SecretStr, constr

ConstrainedStr = object


class APIKey(SecretStr):
    """An API Key used for authenticating and authorizing a client."""

    def __repr__(self) -> str:
        """Return a secure representation of this key."""
        return f"APIKey('{self}')"


PATH_REGEX = r"^[a-zA-Z0-9\._-]{1,128}$"

XSystem = Annotated[str, constr(pattern=PATH_REGEX)]

EntityType = Annotated[str, constr(pattern=PATH_REGEX)]


class UserDatabase(dict[APIKey, list[str]]):
    """A lookup of which x-systems each APIKey is allowed to access."""
