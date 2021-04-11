import json

from flask import Blueprint
from flask_socketio import SocketIO

import utils


def internal_error(e):
    return json.dumps({'status_code': 500, 'message': 'Internal server error'}), 500


class CustomBlueprint(Blueprint):
    data = []
    session_pool: utils.SessionPool
    socketio_clients: dict
    socketio: SocketIO

    def __init__(self, name, import_name, **kwargs):
        super().__init__(name, import_name, **kwargs)
        self.errorhandler(500)(internal_error)

    @classmethod
    def set_properties(cls, **kwargs):
        for k, v in kwargs.items():
            cls.__dict__[k] = v
