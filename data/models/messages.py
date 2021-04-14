from datetime import datetime

from sqlalchemy import Column, orm, Integer, ForeignKey, Boolean, String, DateTime

from data.db_session import SqlAlchemyBase


class MessageModel(SqlAlchemyBase):
    __tablename__ = 'messages'

    id = Column(Integer,
                primary_key=True, autoincrement=True)
    text = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    dialog_id = Column(Integer, ForeignKey('dialogs.id'))
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now)

    dialog = orm.relation('DialogModel', foreign_keys=[dialog_id])
