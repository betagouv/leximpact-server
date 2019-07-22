from dotenv import load_dotenv
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import scoped_session, sessionmaker  # type: ignore

from repo.config import database_url

load_dotenv(dotenv_path=".env")
DB_ENGINE = create_engine(database_url())


def with_session(function):
    def _with_session(*args, **kwargs):
        connection = DB_ENGINE.connect()
        session = scoped_session(sessionmaker(bind=DB_ENGINE))
        result = function(session, *args, **kwargs)
        session.close()
        connection.close()
        return result

    return _with_session
