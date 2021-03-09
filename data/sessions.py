from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from .db_session import SqlAlchemyBase


class Session(SqlAlchemyBase):
    __tablename__ = 'sessions'

    id = Column(Integer,
                primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    fingerprint = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
    refresh_token = Column(String)

    access_token = None
