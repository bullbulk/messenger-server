import json
from typing import List

import eventlet
from flask import Flask, request, g
from flask_socketio import SocketIO, emit

from data import db_session
from data.constants import *
from data.models import dialogs, messages
from utils import match_required_params, SessionPool

eventlet.monkey_patch()

app = Flask(__name__)

session_pool = SessionPool()
socketio_clients = {}

app.session_pool = session_pool
app.socketio_client = socketio_clients

socketio = SocketIO(app, async_mode='eventlet')


@app.errorhandler(500)
def internal_error(e):
    return json.dumps({'status_code': 500, 'message': 'Internal server error'}), 500


@app.route('/')
@app.route('/index')
def index():
    return 'There is no index page'


@app.route('/dialog/send', methods=['POST'])
def create_dialog():
    data = request.json
    session = db_session.create_session()

    if not match_required_params(data, ['member_ids', 'access_token']):
        return NOT_ENOUGH_ARGS.json()
    access_token = data.get('access_token')

    is_token_valid = session_pool.check_access_token(access_token)
    if not is_token_valid:
        return INVALID_ACCESS_TOKEN.json()

    ids: List = data.get('member_ids', [])

    if not ids:
        return INVALID_PARAMETER.json()

    ids: str = json.dumps(sorted(list(map(int, ids))))
    if session.query(dialogs.DialogModel).filter(dialogs.DialogModel.members_id == ids).all():
        return ITEM_ALREADY_EXISTS.json()

    dialog = dialogs.DialogModel()
    dialog.members_id = ids

    session.add(dialog)
    session.commit()
    return SUCCESS.json()


@app.route('/message/send', methods=['POST'])
def send_message():
    data = request.json

    if not match_required_params(list(data.keys()), ['text', 'access_token', 'addressee_id']):
        return NOT_ENOUGH_ARGS.json()
    text = data.get('text')
    access_token = data.get('access_token')
    addressee_id = data.get('addressee_id')

    is_token_valid = session_pool.check_access_token(access_token)
    if not is_token_valid:
        return INVALID_ACCESS_TOKEN.json()
    session = db_session.create_session()

    message = messages.MessageModel()
    message.text = text
    message.addressee_id = addressee_id
    message.author_id = data.get('author_id')
    ids = sorted(list(map(int, [message.author_id, message.addressee_id])))
    q = session.query(dialogs.DialogModel).filter(dialogs.DialogModel.members_id == json.dumps(ids))
    if not q.all():
        return NOT_FOUND.json()
    dialog = q.first()

    message.dialog_id = dialog.id

    if addressee_id in socketio_clients:
        emit('new_message', {'data': 'message'}, room=socketio_clients[addressee_id], namespace='/')

    session.add(message)
    session.commit()
    return SUCCESS.json()


@socketio.on('register_callback')
def callback(message):
    user_id = message['user_id']

    socketio_clients[user_id] = request.sid
    emit('status', {'data': 'success'})
