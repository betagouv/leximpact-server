from os import getenv
from dotenv import load_dotenv
from typing import Optional

load_dotenv(dotenv_path=".env")

ENV = [
    "DATABASE_USER",
    "DATABASE_PASS",
    "DATABASE_HOST",
    "DATABASE_PORT",
    "DATABASE_NAME",
    "DATABASE_URL",
]


def database_config():
    return tuple(getenv(env) for env in ENV)


def database_url(env: Optional[str] = None) -> str:
    user, pswd, host, port, name, url = database_config()

    if url:
        return url

    if env:
        return f"postgresql://{user}:{pswd}@{host}:{port}/{name}_{env}"

    return f"postgresql://{user}:{pswd}@{host}:{port}/{name}_development"
