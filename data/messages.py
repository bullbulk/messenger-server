from datetime import datetime

from sqlalchemy import Column, orm, Integer, ForeignKey, Boolean, String, DateTime

from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase):
    __tablename__ = 'messages'

    id = Column(Integer,
                primary_key=True, autoincrement=True)
    text = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    addressee_id = Column(Integer, ForeignKey('users.id'))
    dialog_id = Column(Integer, ForeignKey('dialogs.id'))
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now)

    user = orm.relation('User', foreign_keys=[addressee_id])
    dialog = orm.relation('Dialog', foreign_keys=[dialog_id])
