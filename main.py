from flask import Flask

from data import db_session

app = Flask(__name__)


def main():
    db_session.global_init("db/messenger.db")


if __name__ == '__main__':
    main()
