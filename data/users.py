import datetime

import sqlalchemy
from sqlalchemy import Column

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(sqlalchemy.Integer,
                primary_key=True, autoincrement=True)
    nickname = Column(sqlalchemy.String)
    email = Column(sqlalchemy.String,
                   index=True, unique=True)
    hashed_password = Column(sqlalchemy.String)
    modified_date = Column(sqlalchemy.DateTime,
                           default=datetime.datetime.now)
    created_date = Column(sqlalchemy.DateTime)
