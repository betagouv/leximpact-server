from sqlalchemy import Column, String, DateTime, Integer  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from typing import Any
import datetime

Base: Any = declarative_base()


class RequestResult(Base):
    __tablename__ = "request_result"
    id_request = Column(String())
    status = Column(String())
    result = Column(String())


def create_request_result(session, id_req):
    request = RequestResult(id_request=id_req, status="created")
    session.add(request)
    session.commit()
    return True


def get_request_result(session, id_req):
    return session.query(RequestResult).get(id_req)


def update_request_result(
    session, new_status, new_result=None
) -> Optional[RequestResult]:
    request_result = get_request_result(session, email)
    if request_result is not None:
        request_result.status = new_status
        if new_result is not None:
            request_result.result = new_result
        session.commit()
        return request_result
    else:
        return None
