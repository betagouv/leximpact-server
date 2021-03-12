from typing import Any

from sqlalchemy import Column, String  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from server.services.database_services import with_session  # type: ignore

SETUP = "server.services.database_services.setup"


def test_with_session(mocker, setup):
    mocker.patch(SETUP, return_value=setup())

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
