from typing import List

from flask import request

from blueprints.custom_bp import CustomBlueprint
from data import db_session
from data.constants import *
from data.models.chats import ChatModel
from data.models.messages import MessageModel
from utils import match_required_params

bp = CustomBlueprint(
    'chats_api',
    __name__,
    url_prefix='/chats'
)


@bp.route('/create', methods=['POST'])
def create_chat():
    data = request.json
    session = db_session.create_session()

    if not match_required_params(data, ['members_id', 'access_token']):
        return NOT_ENOUGH_ARGS.json()
    access_token = data.get('access_token')

    is_token_valid = bp.session_pool.check_access_token(access_token)
    if not is_token_valid:
        return INVALID_ACCESS_TOKEN.json()

    ids: List = sorted(data.get('members_id', []))

    if not ids:
        return INVALID_PARAMETER.json()

    if session.query(ChatModel).filter(ChatModel.members_id == ids).all():
        return ITEM_ALREADY_EXISTS.json()

    chat = ChatModel()
    chat.members_id = ids

    session.add(chat)
    session.commit()
    return SUCCESS.json()


@bp.route('/all', methods=['POST'])
def get_all_chats():
    data = request.json

    if not match_required_params(list(data.keys()), ['user_id', 'access_token']):
        return NOT_ENOUGH_ARGS.json()

    user_id = data.get('user_id')
    access_token = data.get('access_token')

    is_token_valid = bp.session_pool.check_access_token(access_token)
    if not is_token_valid:
        return INVALID_ACCESS_TOKEN.json()

    session = db_session.create_session()
    chats = session.query(ChatModel).filter(ChatModel.members_id.contains(user_id))

    res = SUCCESS.copy()
    res['data'] = {'chats': chats}
    return SUCCESS.json()


@bp.route('/messages', methods=['POST'])
def get_messages():
    data = request.json

    if not match_required_params(list(data.keys()), ['chat_id', 'access_token']):
        return NOT_ENOUGH_ARGS.json()

    session = db_session.create_session()
    messages = session.query(MessageModel) \
        .filter(MessageModel.chat_id == data['chat_id']) \
        .with_entities(MessageModel.id, MessageModel.text).all()
    res = SUCCESS.copy()
    res['data'] = {'messages': messages}
    return res.json()
