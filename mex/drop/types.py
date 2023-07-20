import re

from pydantic import ConstrainedStr, SecretStr


class APIKey(SecretStr):
    """An API Key used for authenticating and authorizing a client."""

    def __repr__(self) -> str:
        """Return a secure representation of this key."""
        return f"APIKey('{self}')"


class XSystem(ConstrainedStr):
    """The identifier of the x-system the dropped data belongs to.

    Allowed characters: a-z, A-Z, 0-9, -, _
    """

    regex = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")


class EntityType(ConstrainedStr):
    """The type of the entities provided in the dropped data.

    Allowed characters: a-z, A-Z, 0-9, -, _
    """

    regex = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")


class UserDatabase(dict[APIKey, list[XSystem]]):
    """A lookup of which x-systems each APIKey is allowed to access."""
