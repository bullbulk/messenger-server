import datetime

from sqlalchemy import Column, String, Integer, DateTime

from data.db_session import SqlAlchemyBase


class UserModel(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String, unique=True, index=True)
    email = Column(String, index=True, unique=True)
    hashed_password = Column(String)
    modified_date = Column(DateTime,
                           default=datetime.datetime.now)
    created_date = Column(DateTime)
