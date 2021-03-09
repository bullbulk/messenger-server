import datetime as dt
import secrets

import config
from data import db_session
from data.sessions import Session


def _create_unique_token(tokens):
    while (token := _create_token()) in tokens:
        pass
    else:
        return token


def _create_token():
    return secrets.token_hex(config.token_length)


class AccessTokenPool:
    valid_tokens = []
    tokens_expire_date = {}

    def create_new_token(self):
        token = _create_unique_token(self.valid_tokens)
        self.valid_tokens.append(token)
        date = dt.datetime.now()
        expire_date = date + dt.timedelta(0, config.access_token_expire_sec)
        self.tokens_expire_date[token] = expire_date
        return token

    def is_expired(self, token):
        if token not in self.valid_tokens:
            return True
        if dt.datetime.now() > self.tokens_expire_date[token]:
            self.remove_token(token)
            return True
        return False

    def remove_token(self, token):
        if token in self.valid_tokens:
            self.valid_tokens.remove(token)
        if token in self.tokens_expire_date.keys():
            self.tokens_expire_date.pop(token)


class UsersPool:
    token_pool = AccessTokenPool()
    access_tokens = {}

    def create_access_token(self, fingerprint):
        if token := self.access_tokens.get(fingerprint):
            self.token_pool.remove_token(token)

        token = self.token_pool.create_new_token()
        self.access_tokens[fingerprint] = token
        return token

    def create_new_session(self, user_id: int, fingerprint):
        session = Session()
        session.fingerprint = fingerprint
        session.refresh_token = _create_token()
        session.expires_at = dt.datetime.now() + dt.timedelta(seconds=config.refresh_token_expire_sec)
        session.user_id = user_id

        db_sess = db_session.create_session()
        db_sess.add(session)
        db_sess.commit()

        return session

    def is_valid_access_token(self, token):
        return not self.token_pool.is_expired(token)

    @classmethod
    def is_valid_refresh_token(cls, token):
        db_sess = db_session.create_session()
        session = db_sess.query(Session).filter(Session.refresh_token == token).first()
        if dt.datetime.now() > session.expires_at:
            return False
        return True

    def get_session(self, user_id, fingerprint):
        db_sess = db_session.create_session()
        q = db_sess.query(Session)
        q = q.filter(Session.user_id == user_id, Session.fingerprint == fingerprint,
                     dt.datetime.now() < Session.expires_at)
        if q.all():
            session = q.first()
            session.access_token = self.create_access_token(fingerprint)
            return q.first()

        session = self.create_new_session(user_id, fingerprint)
        session.access_token = self.create_access_token(fingerprint)
        return session
