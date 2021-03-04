from psycopg2 import connect, errors  # type: ignore
from repo.config import database_config

user, pswd, host, port, name, url = database_config()
print(f"DEBUG : connect(user={user}, password=XXXX, host={host}, port={port}, database={name})")
connexion = connect(user=user, password=pswd, host=host, port=port, database=name)
connexion.autocommit = True
cursor = connexion.cursor()

try:
    cursor.execute(f"CREATE DATABASE {name}_development")
    cursor.execute(f"CREATE DATABASE {name}_test")
except errors.DuplicateDatabase:
    pass
