from dotenv import load_dotenv
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import scoped_session, sessionmaker  # type: ignore

from repo.config import database_url

load_dotenv(dotenv_path=".env")


def with_session(function):
    def _with_session(*args, **kwargs):
        engine, connection, session = setup()
        connection = engine.connect()
        session = scoped_session(sessionmaker(bind=engine))
        result = function(session, *args, **kwargs)
        cleanup(session, connection)
        connection.close()
        return result

    return _with_session


def setup():
    engine = create_engine(database_url())
    connection = engine.connect()
    session = scoped_session(sessionmaker(bind=engine))
    return engine, connection, session


def cleanup(session, connection):
    session.close()
    connection.close()
