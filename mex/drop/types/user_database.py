from pydantic import SecretStr

UserDatabase = dict[SecretStr, list[SecretStr]]
