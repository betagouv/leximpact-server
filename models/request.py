from sqlalchemy import Column, String, DateTime, Integer  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from typing import Any, Optional
import datetime

Base: Any = declarative_base()


class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True)
    email = Column(String())
    timestamp = Column(DateTime())


def create_request(session, email):
    request = Request(email=email, timestamp=datetime.datetime.now())
    session.add(request)
    session.commit()
    return True
