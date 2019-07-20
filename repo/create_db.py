from psycopg2 import connect, errors  # type: ignore
from repo.config import database_config

user, pswd, host, port, name, _ = database_config()
connexion = connect(user=user, password=pswd, host=host, port=port)
connexion.autocommit = True
cursor = connexion.cursor()

try:
    cursor.execute(f"CREATE DATABASE {name}_development")
    cursor.execute(f"CREATE DATABASE {name}_test")
except errors.DuplicateDatabase:
    pass
