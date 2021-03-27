import secrets

import config
import datetime as dt


def generate_unique_token(tokens):
    while (token := generate_token()) in tokens:
        pass
    else:
        return token


def generate_token():
    return secrets.token_hex(config.token_length)


class Token:
    token: str
    expire_date: dt.datetime

    def __init__(self, token, expire_date):
        self.token = token
        self.expire_date = expire_date

    def is_expired(self):
        if dt.datetime.now() > self.expire_date:
            return True
        return False

