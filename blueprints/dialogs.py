import json
from typing import List

from flask import request

from blueprints.custom_bp import CustomBlueprint
from data import db_session
from data.constants import *
from data.models import dialogs
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
