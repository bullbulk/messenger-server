import datetime

import sqlalchemy
from sqlalchemy import Column

from .db_session import SqlAlchemyBase


class Dialog(SqlAlchemyBase):
    __tablename__ = 'dialogs'

    id = Column(sqlalchemy.Integer,
                primary_key=True, autoincrement=True)
    first_member_id = Column(sqlalchemy.Integer)
    second_member_id = Column(sqlalchemy.Integer)
    hashed_password = Column(sqlalchemy.String)
    created_date = Column(sqlalchemy.DateTime, default=datetime.datetime.now)
