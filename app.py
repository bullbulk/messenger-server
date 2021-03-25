import json
from datetime import datetime
from typing import List

import sqlalchemy
from flask import Flask, request, jsonify

from data import db_session
from data.constants import *
from data.models import dialogs, users
from data.models.sessions import Session
from utils import match_required_params, UsersPool

app = Flask(__name__)

users_pool = UsersPool()


@app.route('/')
@app.route('/index')
def index():
    return 'There is no index page'


@app.route('/create_dialog', methods=['POST'])
def create_dialog():
    args = request.args
    session = db_session.create_session()

    if not match_required_params(args, ['ids']):
        return NOT_ENOUGH_ARGS.json()
    ids: List = args.getlist('ids')[:2]

    ids = sorted(list(map(int, ids)))
    if session.query(dialogs.Dialog).filter(dialogs.Dialog.members_id == json.dumps(ids)).all():
        return ITEM_ALREADY_EXISTS.json()

    dialog = dialogs.Dialog()
    dialog.members_id = json.dumps(ids)

    session.add(dialog)
    session.commit()
    return SUCCESS.json()


@app.route('/register_user', methods=['POST'])
def register_user():
    session = db_session.create_session()

    args = request.args
    user = users.User()

    if not match_required_params(args, ['nickname', 'email', 'password']):
        print(args)
        return NOT_ENOUGH_ARGS.json()
    user.nickname = args.get('nickname')
    user.email = args.get('email')
    # user.hashed_password = utils.encrypt_password(args.get('password'))
    user.hashed_password = args.get('password')

    if session.query(users.User).filter(
            sqlalchemy.or_(users.User.email == args.get('email'))).all():
        res = ITEM_ALREADY_EXISTS.copy()
        res['reason'] = 'email'
        return ITEM_ALREADY_EXISTS.json()
    if session.query(users.User).filter(
            sqlalchemy.or_(users.User.nickname == args.get('nickname'))).all():
        res = ITEM_ALREADY_EXISTS.copy()
        res['reason'] = 'nickname'
        return ITEM_ALREADY_EXISTS.json()

    user.created_date = datetime.now()

    session.add(user)
    session.commit()
    return SUCCESS.json()


@app.route('/auth_user', methods=['GET'])
def authenticate():
    args = request.args

    if not match_required_params(args, ['email', 'password', 'fingerprint']):
        return NOT_ENOUGH_ARGS.json()
    email = args.get('email')
    password = args.get('password')
    fingerprint = args.get('fingerprint')

    session = db_session.create_session()
    query = session.query(users.User).filter(users.User.email == email)
    if not query.all():
        return NOT_FOUND.json()
    user = query.first()
    is_matched_password = password == user.hashed_password

    if is_matched_password:
        resp = SUCCESS.copy()
        session = users_pool.get_session(user.id, fingerprint)
        resp['access_token'] = session.access_token
        resp['refresh_token'] = session.refresh_token
    else:
        resp = UNAUTHORIZED
    return resp.json()


@app.route('/send_message', methods=['POST'])
def send_message():
    args = request.args

    if not match_required_params(list(args.keys()), ['text', 'token', 'addressee_id']):
        return NOT_ENOUGH_ARGS.json()
    text = args.get('text')
    token = args.get('token')
    addressee_id = args.get('addressee_id')

    is_token_valid = users_pool.is_valid_access_token(token)
    if not is_token_valid:
        return INVALID_ACCESS_TOKEN.json()
    return SUCCESS.json()


@app.route('/get_tokens')  # FOR DEBUG
def get_tokens():
    return jsonify([users_pool.access_tokens, users_pool.token_pool.valid_tokens,
                    users_pool.token_pool.tokens_expire_date])


@app.route('/get_access_token')
def get_access_token():
    args = request.args

    if not match_required_params(list(args.keys()), ['fingerprint', 'refresh_token']):
        return NOT_ENOUGH_ARGS.json()

    fingerprint = args.get('fingerprint')
    refresh_token = args.get('refresh_token')

    db_sess = db_session.create_session()
    query = db_sess.query(Session).filter(Session.fingerprint == fingerprint, Session.refresh_token == refresh_token)

    if not query.all():
        return INVALID_REFRESH_TOKEN.json()
    session = query.first()
    if not users_pool.is_valid_refresh_token(session.refresh_token):
        return INVALID_REFRESH_TOKEN.json()

    token = users_pool.create_access_token(fingerprint)
    resp = SUCCESS.copy()
    resp['access_token'] = token
    return resp.json()
