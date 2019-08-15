from sqlalchemy import Column, String, DateTime, Integer  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from typing import Any
import datetime

Base: Any = declarative_base()


class Suspended(Base):
    __tablename__ = "suspended"
    id = Column(Integer, primary_key=True)
    email = Column(String())
    end_suspension = Column(DateTime())


def create_suspension(session, email, delay_hours=1):
    suspended = Suspended(
        email=email,
        end_suspension=datetime.datetime.now() + datetime.timedelta(hours=delay_hours),
    )
    session.add(suspended)
    session.commit()
    return True


def count_active_suspensions(session, email):
    return (
        session.query(Suspended)
        .filter(
            Suspended.email == email, Suspended.end_suspension > datetime.datetime.now()
        )
        .count()
    )
