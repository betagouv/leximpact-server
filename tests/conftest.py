from pytest import fixture  # type: ignore

from server.app import app  # type: ignore
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import scoped_session, sessionmaker  # type: ignore
from repo.config import database_url  # type: ignore
from models import User  # type: ignore


@fixture
def client():
    app.config["TESTING"] = True
    client = app.test_client()
    return client


@fixture
def mimetype() -> str:
    return "application/json"


@fixture
def headers(mimetype: str) -> dict:
    return {"Content-Type": mimetype, "Accept": mimetype}


@fixture
def setup():
    def _setup():
        engine = create_engine(database_url("test"))
        connection = engine.connect()
        session = scoped_session(sessionmaker(bind=engine))
        return engine, connection, session

    return _setup


@fixture
def cleanup():
    def _cleanup(session, connection):
        session.query(User).delete()
        session.commit()
        session.close()
        connection.close()

    return _cleanup


@fixture
def session(setup, cleanup):
    engine, connection, session = setup()
    yield session
    cleanup(session, connection)
