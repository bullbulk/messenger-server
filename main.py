from app import app, socketio, session_pool
from blueprints import user
from data import db_session


def share_variables():
    user.bp.set_data({'session_pool': session_pool})


def main():
    db_session.global_init("db/messenger.db")
    app.register_blueprint(user.bp)
    share_variables()
    socketio.run(app, '127.0.0.1', port=9999, debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
