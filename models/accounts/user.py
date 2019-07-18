from sqlalchemy import Column, String  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from typing import Any

Base: Any = declarative_base()


class User(Base):
    __tablename__ = 'users'
    email = Column(String(), primary_key=True)
    token = Column(String())
