import json

import eventlet
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import cross_origin

from utils import SessionPool

eventlet.monkey_patch()

app = Flask(__name__)

session_pool = SessionPool()
socketio_clients = {}

socketio = SocketIO(app, async_mode='eventlet')


@app.errorhandler(500)
def internal_error(e):
    return json.dumps({'status_code': 500, 'message': 'Internal server error'}), 500


@app.route('/')
@app.route('/index')
@cross_origin()
def index():
    return 'There is no index page'


@socketio.on('register_callback')
def callback(message):
    user_id = message['user_id']

    socketio_clients[user_id] = request.sid
    emit('status', {'data': 'success'})
