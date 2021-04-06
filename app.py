import json
from datetime import datetime
from typing import List

import eventlet
from flask import Flask, request
from flask_socketio import SocketIO, emit

from data import db_session
from data.constants import *
from data.models import dialogs, users, messages, sessions
from utils import match_required_params, SessionPool

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

session_pool = SessionPool()
socket_clients = {}


@app.route('/')
@app.route('/index')
def index():
    return 'There is no index page'


@app.route('/create_dialog', methods=['POST'])
def create_dialog():
    data = request.json
    session = db_session.create_session()

    if not match_required_params(data, ['ids', 'access_token']):
        return NOT_ENOUGH_ARGS.json()
    access_token = data.get('access_token')
    addressee_id = data.get('addressee_id')

    is_token_valid = session_pool.check_access_token(access_token)
    if not is_token_valid:
        return INVALID_ACCESS_TOKEN.json()

    ids: List = data.get('ids')[:2]

    ids = sorted(list(map(int, ids)))
    if session.query(dialogs.DialogModel).filter(dialogs.DialogModel.members_id == json.dumps(ids)).all():
        return ITEM_ALREADY_EXISTS.json()

    dialog = dialogs.DialogModel()
    dialog.members_id = json.dumps(ids)

    session.add(dialog)
    session.commit()
    return SUCCESS.json()


@app.route('/register', methods=['POST'])
def register_user():
    session = db_session.create_session()

    data = request.json
    user = users.UserModel()

    if not match_required_params(data, ['nickname', 'email', 'password']):
        return NOT_ENOUGH_ARGS.json()
    user.nickname = data.get('nickname')
    user.email = data.get('email')
    user.hashed_password = data.get('password')

    if session.query(users.UserModel).filter(users.UserModel.email == data.get('email')).all():
        res = ITEM_ALREADY_EXISTS.copy()
        res['reason'] = 'email'
        return res.json()
    if session.query(users.UserModel).filter(users.UserModel.nickname == data.get('nickname')).all():
        res = ITEM_ALREADY_EXISTS.copy()
        res['reason'] = 'nickname'
        return res.json()

    user.created_date = datetime.now()

    session.add(user)
    session.commit()
    return SUCCESS.json()


@app.route('/login', methods=['POST'])
def login():
    data = request.json

    if not match_required_params(data, ['email', 'password', 'fingerprint']):
        return NOT_ENOUGH_ARGS.json()
    email = data.get('email')
    password = data.get('password')
    fingerprint = data.get('fingerprint')

    session = db_session.create_session()
    query = session.query(users.UserModel).filter(users.UserModel.email == email)
    if not query.all():
        return NOT_FOUND.json()
    user = query.first()
    is_matched_password = password == user.hashed_password

    if is_matched_password:
        resp = SUCCESS.copy()
        session = session_pool.create_new(user.id, fingerprint)
        resp['access_token'] = session.access_token
        resp['refresh_token'] = session.refresh_token
        resp['user_id'] = user.id
    else:
        resp = UNAUTHORIZED
    return resp.json()


@app.route('/send_message', methods=['POST'])
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
    message.author_id = session.query(sessions.SessionModel).filter(
        sessions.SessionModel.fingerprint == session_pool.get_user_fp(access_token)).first().user_id

    ids = sorted(list(map(int, [message.author_id, message.addressee_id])))
    q = session.query(dialogs.DialogModel).filter(dialogs.DialogModel.members_id == json.dumps(ids))
    if not q.all():
        return NOT_FOUND.json()
    dialog = q.first()

    message.dialog_id = dialog.id

    if addressee_id in socket_clients:
        socket_clients[addressee_id].emit('new_message', {'data': {'dialog': dialog.id}})

    return SUCCESS.json()


@app.route('/get_access_token', methods=['POST'])
def get_access_token():
    data = request.json

    if not match_required_params(list(data.keys()), ['fingerprint', 'refresh_token']):
        return NOT_ENOUGH_ARGS.json()

    refresh_token = data.get('refresh_token')

    new_session = session_pool.update_session(refresh_token)

    if not new_session:
        return INVALID_REFRESH_TOKEN.json()
    print(session_pool.access_token_pool.valid_tokens)

    resp = SUCCESS.copy()
    resp['access_token'] = new_session.access_token
    resp['refresh_token'] = new_session.refresh_token
    return resp.json()


@socketio.on('register_callback')
def callback(message):
    user_id = message['user_id']

    socket_clients[user_id] = request.namespace
    emit('status', {'data': 'success'})
