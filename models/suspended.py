from sqlalchemy import Column, String, DateTime, Integer  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
#from server.services import send_mail # TODO : make this import work !
from typing import Any
import logging
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
    alert_suspension(email, delay_hours)
    return True

def count_active_suspensions(session, email):
    return (
        session.query(Suspended)
        .filter(
            Suspended.email == email, Suspended.end_suspension > datetime.datetime.now()
        )
        .count()
    )

def alert_suspension(email, delay_hours):
    email_team='benoit.courty@assemblee-nationale.fr'
    content_team  = f"Bonjour\nL'utilisateur {email} vient d'être suspendu pour {delay_hours} heure(s).\nVotre dévoué serveur LexImpact"
    print(content_team)
    logging.error(f"BRUTE FORCE STOPPED : {content_team}")
    send_mail(
            recipient=email_team,
            subject="Nouvelle suspension",
            content=content_team,
        )
    send_mail(
            recipient=email,
            subject="Compte LexImpact suspendu",
            content=f"Bonjour\nVotre compte LexImpact vient d'être suspendu pour {delay_hours} heure(s) en raison d'une utilisation trop importante.\nMerci de votre compréhension,\nL'équipe LexImpact",
        )
    return True