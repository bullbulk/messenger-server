from app import app, socketio
from data import db_session


def main():
    db_session.global_init("db/messenger.db")
    socketio.run(app, '127.0.0.1', port=9999, debug=True)


if __name__ == '__main__':
    main()
