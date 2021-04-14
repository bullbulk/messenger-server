import json

from flask import request

from blueprints.custom_bp import CustomBlueprint
from data import db_session
from data.constants import *
from data.models import messages, dialogs
from utils import match_required_params

bp = CustomBlueprint(
    'messages_api',
    __name__,
    url_prefix='/messages'
)


@bp.route('/send', methods=['POST'])
def send_message():
    data = request.json

    if not match_required_params(list(data.keys()), ['text', 'access_token', 'dialog_id']):
        return NOT_ENOUGH_ARGS.json()
    text = data.get('text')
    access_token = data.get('access_token')
    dialog_id = data.get('dialog_id')

    is_token_valid = bp.session_pool.check_access_token(access_token)
    if not is_token_valid:
        return INVALID_ACCESS_TOKEN.json()
    session = db_session.create_session()

    message = messages.MessageModel()
    message.text = text
    message.author_id = data.get('author_id')
    q = session.query(dialogs.DialogModel).filter(dialogs.DialogModel.id == dialog_id)
    if not q.all():
        return NOT_FOUND.json()
    dialog = q.first()

    message.dialog_id = dialog.id

    for i in dialog.members_id:
        if i in bp.socketio_clients:
            bp.socketio.emit('new_message', {'data': 'message'}, room=bp.socketio_clients[i], namespace='/')

    session.add(message)
    session.commit()
    return SUCCESS.json()