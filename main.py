from app import app
from data import db_session


def main():
    db_session.global_init("db/messenger.db")
    app.run('127.0.0.1', port=9999)


if __name__ == '__main__':
    main()
