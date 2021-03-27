import datetime as dt
from typing import Dict

import config
from data import db_session
from data.models.sessions import SessionModel
from utils.token import generate_token, generate_unique_token, Token


def create_new_session(user_id: int, fingerprint):
    session = SessionModel()
    session.fingerprint = fingerprint
    session.refresh_token = generate_token()
    session.expires_at = dt.datetime.now() + dt.timedelta(seconds=config.refresh_token_expire_sec)
    session.user_id = user_id

    db_sess = db_session.create_session()
    db_sess.add(session)
    db_sess.commit()

    return session


class Session:
    def __init__(self, user_id: int, fingerprint: str):
        self.model = SessionModel()
        self.user_id = user_id
        self.fingerprint = fingerprint


class AccessTokenPool:
    valid_tokens: Dict[str, Token] = {}

    def create_new_token(self, fingerprint):
        token = generate_unique_token(self.valid_tokens)
        date = dt.datetime.now()
        expire_date = date + dt.timedelta(0, config.access_token_expire_sec)
        token_data = Token(token, expire_date)
        self.valid_tokens[fingerprint] = token_data
        return token_data

    def get_token_key(self, token):
        tokens = list(self.valid_tokens.values())
        if token not in tokens:
            return
        index = tokens.index(token)
        return list(self.valid_tokens.keys())[index]

    def remove_token(self, token: Token):
        if token in self.valid_tokens:
            del self.valid_tokens[self.get_token_key(token)]

    def remove_token_by_key(self, key: str):
        del self.valid_tokens[key]

    def is_valid(self, _token: str):
        token = self.get_token_instance(_token)
        if not token:
            return False
        if token.is_expired():
            self.remove_token(token)
            return False
        return True

    def get(self, fingerprint):
        return self.valid_tokens.get(fingerprint)

    def get_token_instance(self, _token: str):
        token = list(filter(lambda x: x.token == _token, self.valid_tokens.values()))
        if not token:
            return
        return token[0]


class SessionPool:
    sessions = []

    def __init__(self):
        self.access_token_pool = AccessTokenPool()

    def create_access_token(self, fingerprint):
        if token := self.access_token_pool.get(fingerprint):  # remove token if it valid
            self.access_token_pool.remove_token(token)

        token = self.access_token_pool.create_new_token(fingerprint)
        return token

    def create_new(self, user_id, fingerprint):
        db_sess = db_session.create_session()
        q = db_sess.query(SessionModel)
        q = q.filter(SessionModel.user_id == user_id, SessionModel.fingerprint == fingerprint,
                     dt.datetime.now() < SessionModel.expires_at)
        if q.all():
            session = q.first()
            session.access_token = self.create_access_token(fingerprint).token
            return q.first()

        session = create_new_session(user_id, fingerprint)
        session.access_token = self.create_access_token(fingerprint).token
        self.sessions.append(session)
        return session

    def update_session(self, refresh_token):
        db_sess = db_session.create_session()
        q = db_sess.query(SessionModel)
        q = q.filter(SessionModel.refresh_token == refresh_token)
        if not q.all():
            return
        session = q.first()
        if Token(session.refresh_token, session.expires_at).is_expired():
            return

        db_sess.delete(session)
        db_sess.commit()
        self.access_token_pool.remove_token_by_key(session.fingerprint)
        new_session = self.create_new(session.user_id, session.fingerprint)
        db_sess.object_session(new_session).add(new_session)
        db_sess.commit()
        return new_session


    def check_access_token(self, token: str):
        return self.access_token_pool.is_valid(token)
