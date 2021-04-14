from typing import List

from flask import request

from blueprints.custom_bp import CustomBlueprint
from data import db_session
from data.constants import *
from data.models.dialogs import DialogModel
from data.models.messages import MessageModel
from utils import match_required_params

bp = CustomBlueprint(
    'dialogs_api',
    __name__,
    url_prefix='/dialogs'
)


@bp.route('/create', methods=['POST'])
def create_dialog():
    data = request.json
    session = db_session.create_session()

    if not match_required_params(data, ['member_ids', 'access_token']):
        return NOT_ENOUGH_ARGS.json()
    access_token = data.get('access_token')

    is_token_valid = bp.session_pool.check_access_token(access_token)
    if not is_token_valid:
        return INVALID_ACCESS_TOKEN.json()

    ids: List = sorted(data.get('member_ids', []))

    if not ids:
        return INVALID_PARAMETER.json()

    if session.query(DialogModel).filter(DialogModel.members_id == ids).all():
        return ITEM_ALREADY_EXISTS.json()

    dialog = DialogModel()
    dialog.members_id = ids

    session.add(dialog)
    session.commit()
    return SUCCESS.json()


@bp.route('/all', methods=['POST'])
def get_all_dialogs():
    data = request.json

    if not match_required_params(list(data.keys()), ['user_id', 'access_token']):
        return NOT_ENOUGH_ARGS.json()

    user_id = data.get('user_id')
    access_token = data.get('access_token')

    is_token_valid = bp.session_pool.check_access_token(access_token)
    if not is_token_valid:
        return INVALID_ACCESS_TOKEN.json()

    session = db_session.create_session()
    dialogs = session.query(DialogModel).filter(DialogModel.members_id.contains(user_id))

    res = SUCCESS.copy()
    res['data'] = {'dialogs': dialogs}
    return SUCCESS.json()


@bp.route('/messages', methods=['POST'])
def get_messages():
    data = request.json

    if not match_required_params(list(data.keys()), ['dialog_id', 'access_token']):
        return NOT_ENOUGH_ARGS.json()

    session = db_session.create_session()
    messages = session.query(MessageModel) \
        .filter(MessageModel.dialog_id == data['dialog_id']) \
        .with_entities(MessageModel.id, MessageModel.text).all()
    res = SUCCESS.copy()
    res['data'] = {'messages': messages}
    return res.json()
