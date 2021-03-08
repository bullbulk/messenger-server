import json
from datetime import datetime
from typing import List

import sqlalchemy
from flask import Flask, request, jsonify

import utils
from utils import generate_response

from data import db_session, users
from data import dialogs

app = Flask(__name__)


def main():
    db_session.global_init("db/messenger.db")
    app.run('127.0.0.1', port=8080)


@app.route('/create_dialog', methods=['POST'])
def create_dialog():
    args = request.args
    session = db_session.create_session()

    if not utils.match_required_fields(args, ['ids']):
        return generate_response(400, **dict(message='Not enough arguments'))
    ids: List = args.getlist('ids')

    ids = list(map(int, ids))
    ids.sort()
    if session.query(dialogs.Dialog).filter(dialogs.Dialog.members_id == json.dumps(ids)).all():
        return generate_response(409, **dict(message='Dialog already exists'))


    dialog = dialogs.Dialog()
    dialog.members_id = json.dumps(ids)

    session.add(dialog)
    session.commit()
    return generate_response(200)


@app.route('/register_user', methods=['POST'])
def register_user():
    session = db_session.create_session()

    args = request.args
    user = users.User()

    if not utils.match_required_fields(args, ['nickname', 'email', 'password']):
        return generate_response(400, **dict(message='Not enough arguments'))
    user.nickname = args.get('nickname')
    user.email = args.get('email')
    user.hashed_password = utils.encrypt_password(args.get('password'))

    if session.query(users.User).filter(
            sqlalchemy.or_(users.User.email == args.get('email'), users.User.nickname == args.get('nickname'))).all():
        return generate_response(409, **dict(message='User already exists'))

    user.created_date = datetime.now()

    session.add(user)
    session.commit()
    return jsonify({'status_code': 200, 'success': True})


@app.route('/auth_user', methods=['GET'])
def authenticate():
    args = request.args

    if not utils.match_required_fields(args, ['email', 'password']):
        return generate_response(400, **dict(message='Not enough arguments'))
    email = args.get('email')
    password = args.get('password')

    session = db_session.create_session()
    query = session.query(users.User).filter(users.User.email == email)
    if not query.all():
        return generate_response(404, **dict(message='User does not exists'))
    user = query.first()
    is_matched_password = utils.match_password(password, user.hashed_password)

    result = {
        'status_code': 200,
        'success': is_matched_password
    }
    return jsonify(result)


if __name__ == '__main__':
    main()
