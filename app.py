import json
from datetime import datetime
from typing import List

import sqlalchemy
from flask import Flask, request, jsonify

import utils
from data import db_session, users
from data import dialogs
from data.constants import *
from data.sessions import Session
from utils import match_required_params

app = Flask(__name__)

users_pool = utils.UsersPool()


@app.route('/')
@app.route('/index')
def index():
    return 404


@app.route('/create_dialog', methods=['POST'])
def create_dialog():
    args = request.args
    session = db_session.create_session()

    if not match_required_params(args, ['ids']):
        return NOT_ENOUGH_ARGS.json()
    ids: List = args.getlist('ids')

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
        return NOT_ENOUGH_ARGS.json()
    user.nickname = args.get('nickname')
    user.email = args.get('email')
    user.hashed_password = utils.encrypt_password(args.get('password'))

    if session.query(users.User).filter(
            sqlalchemy.or_(users.User.email == args.get('email'),
                           users.User.nickname == args.get('nickname'))).all():
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
    is_matched_password = utils.match_password(password, user.hashed_password)

    if is_matched_password:
        resp = SUCCESS.copy()
        session = users_pool.create_new_session(user.id, fingerprint)
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
        return INVALID_TOKEN
    return SUCCESS


@app.route('/get_tokens')  # FOR DEBUG
def get_tokens():
    return jsonify([users_pool.access_tokens, users_pool.token_pool.all_tokens, users_pool.token_pool.expired_tokens,
                    users_pool.token_pool.tokens_expire_date])


@app.route('/get_access_token')
def get_access_token():
    args = request.args

    if not match_required_params(list(args.keys()), ['fingerprint']):
        return NOT_ENOUGH_ARGS.json()

    fingerprint = args.get('fingerprint')

    db_sess = db_session.create_session()
    session = db_sess.query(Session).filter(Session.fingerprint == fingerprint)

    if not users_pool.is_valid_refresh_token(session.fingerprint):
