from utils import generate_response

NOT_ENOUGH_ARGS = generate_response(400, message='Not enough arguments')
ITEM_ALREADY_EXISTS = generate_response(409, message='Item already exists')
SUCCESS = generate_response(200)
NOT_FOUND = generate_response(404, message='Item not found')
UNAUTHORIZED = generate_response(401, message='Wrong password or email')
INVALID_ACCESS_TOKEN = generate_response(401, message='Access token does not exist or expired. '
                                                      'Please, get the new access token via refresh token')
INVALID_REFRESH_TOKEN = generate_response(401, message='Refresh token does not exist or expired. '
                                                       'Please, authenticate again')
