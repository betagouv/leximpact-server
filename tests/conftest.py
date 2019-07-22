import pytest  # type: ignore

from server.app import app  # type: ignore
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import scoped_session, sessionmaker  # type: ignore
from repo.config import database_url  # type: ignore
from models import User  # type: ignore


@pytest.fixture
def client():
    app.config["TESTING"] = True
    client = app.test_client()
    return client


@pytest.fixture
def mimetype() -> str:
    return "application/json"


@pytest.fixture
def headers(mimetype: str) -> dict:
    return {"Content-Type": mimetype, "Accept": mimetype}


@pytest.fixture
def engine():
    return create_engine(database_url("test"))


@pytest.fixture
def session(engine):
    connection = engine.connect()
    session = scoped_session(sessionmaker(bind=engine))
    yield session
    session.query(User).delete()
    session.commit()
    session.close()
    connection.close()
