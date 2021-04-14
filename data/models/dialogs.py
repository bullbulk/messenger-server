import datetime

import sqlalchemy
from sqlalchemy import Column, DateTime, String, JSON

from data.db_session import SqlAlchemyBase


class DialogModel(SqlAlchemyBase):
    __tablename__ = 'dialogs'

    id = Column(sqlalchemy.Integer,
                primary_key=True, autoincrement=True)
    members_id = Column(JSON)
    created_date = Column(DateTime, default=datetime.datetime.now)
