from os import getenv
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

ENV = [
    "DATABASE_USER",
    "DATABASE_PASS",
    "DATABASE_HOST",
    "DATABASE_PORT",
    "DATABASE_NAME",
]


def database_config():
    return tuple(getenv(env) for env in ENV)


def database_url(env: str) -> str:
    user, pswd, host, port, name = database_config()
    return f"postgresql://{user}:{pswd}@{host}:{port}/{name}_{env}"
