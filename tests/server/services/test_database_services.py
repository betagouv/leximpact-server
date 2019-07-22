from typing import Any

from sqlalchemy import Column, String  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from server.services import with_session  # type: ignore
from server.services import database_services  # type: ignore


def test_with_session(engine):
    database_services.DB_ENGINE = engine
    Base: Any = declarative_base()

    class User(Base):
        __tablename__ = "users"
        email = Column(String(), primary_key=True)

    @with_session
    def function(session, user):
        session.add(user)
        session.commit()
        user = session.query(User).get(user.email)
        session.query(User).delete()
        session.commit()
        return user

    assert function(User(email="richard@leximpact.pop"))
