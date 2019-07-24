from sqlalchemy import Column, String  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from typing import Any, Optional

Base: Any = declarative_base()


class User(Base):
    __tablename__ = "users"
    email = Column(String(), primary_key=True)
    token = Column(String())


def find_user(session, email: str) -> Optional[User]:
    return session.query(User).get(email)


def create_user(session, user: User) -> bool:
    session.add(user)
    session.commit()
    return True


def update_user_token(session, email: str, token: str) -> Optional[User]:
    user = find_user(session, email)

    if user:
        user.token = token
        session.commit()
        return user
    else:
        return None
