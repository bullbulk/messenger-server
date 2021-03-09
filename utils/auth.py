import secrets
import datetime as dt

import config


def create_unique_token(tokens):
    while (token := create_token()) in tokens:
        pass
    else:
        return token


def create_token():
    return secrets.token_hex(config.token_length)


class TokenPool:
    valid_tokens = []
    tokens_expire_date = {}
    expired_tokens = []

    def create_new_token(self):
        token = create_unique_token(self.valid_tokens)
        self.valid_tokens.append(token)
        date = dt.datetime.now()
        expire_date = date + dt.timedelta(0, config.token_expire_sec)
        self.tokens_expire_date[token] = expire_date
        print(token)
        return token

    def check_expired(self, token):
        if token in self.expired_tokens or token not in self.valid_tokens:
            return True
        if dt.datetime.now() > self.tokens_expire_date[token]:
            self.remove_token(token)
            return True
        return False

    def remove_token(self, token):
        self.valid_tokens.remove(token)
        self.tokens_expire_date.pop(token)
        self.expired_tokens.append(token)


class UsersPool:
    token_pool = TokenPool()
    authorized_users = {}

    def create_new_session(self, user_id: int):
        if token := self.authorized_users.get(user_id):
            self.token_pool.remove_token(token)

        token = self.token_pool.create_new_token()
        self.authorized_users[user_id] = token
        return token

    def check_token(self, token):
        return self.token_pool.check_expired(token)
