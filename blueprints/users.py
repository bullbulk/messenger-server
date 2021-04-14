from datetime import datetime

from flask import request

from blueprints.custom_bp import CustomBlueprint
from data import db_session
from data.constants import *
from data.models import users
from utils import match_required_params

bp = CustomBlueprint(
    'users_api',
    __name__,
    url_prefix='/users'
)


@bp.route('/register', methods=['POST'])
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


@bp.route('/login', methods=['POST'])
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
        session = bp.session_pool.create_new(user.id, fingerprint)
        resp['access_token'] = session.access_token
        resp['refresh_token'] = session.refresh_token
        resp['user_id'] = user.id
    else:
        resp = UNAUTHORIZED
    return resp.json()


@bp.route('/update_session', methods=['POST'])
def get_access_token():
    data = request.json

    if not match_required_params(list(data.keys()), ['refresh_token']):
        return NOT_ENOUGH_ARGS.json()

    refresh_token = data.get('refresh_token')

    new_session = bp.session_pool.update_session(refresh_token)

    if not new_session:
        return INVALID_REFRESH_TOKEN.json()

    resp = SUCCESS.copy()
    resp['access_token'] = new_session.access_token
    resp['refresh_token'] = new_session.refresh_token
    return resp.json()

