import sqlalchemy
from sqlalchemy import Column, orm, Integer, ForeignKey, Boolean

from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase):
    __tablename__ = 'messages'

    user = orm.relation('User')
    dialog = orm.relation('Dialog')

    id = Column(sqlalchemy.Integer,
                primary_key=True, autoincrement=True)
    text = Column(sqlalchemy.String)
    author_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("users.id"))
    addressee_id = Column(Integer, ForeignKey('users.id'))
    dialog_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('dialogs.id'))
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_date = Column(sqlalchemy.DateTime)
