from sqlalchemy import Column, String  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from typing import Any, Optional

Base: Any = declarative_base()


class User(Base):
    __tablename__ = "users"
    email = Column(String(), primary_key=True)


def find_user(session, email: str) -> Optional[User]:
    return session.query(User).get(email)


def create_user(session, user: User) -> bool:
    session.add(user)
    session.commit()
    return True

