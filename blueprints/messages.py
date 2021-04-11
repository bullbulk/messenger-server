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


@bp.route('/message/send', methods=['POST'])
def send_message():
    data = request.json

    if not match_required_params(list(data.keys()), ['text', 'access_token', 'addressee_id']):
        return NOT_ENOUGH_ARGS.json()
    text = data.get('text')
    access_token = data.get('access_token')
    addressee_id = data.get('addressee_id')

    is_token_valid = bp.session_pool.check_access_token(access_token)
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

    if addressee_id in bp.socketio_clients:
        bp.socketio.emit('new_message', {'data': 'message'}, room=bp.socketio_clients[addressee_id], namespace='/')

    session.add(message)
    session.commit()
    return SUCCESS.json()
