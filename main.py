from app import app, socketio, session_pool, socketio_clients
from blueprints import users, custom_bp, dialogs, messages
from data import db_session


def share_global_variables():
    custom_bp.CustomBlueprint.set_properties(
        session_pool=session_pool,
        socketio_clients=socketio_clients,
        socketio=socketio
    )


def set_blueprints():
    app.register_blueprint(users.bp)
    app.register_blueprint(dialogs.bp)
    app.register_blueprint(messages.bp)


def main():
    db_session.global_init("db/messenger.db")

    set_blueprints()
    share_global_variables()

    socketio.run(app, '127.0.0.1', port=9999, debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
