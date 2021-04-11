from utils import Response

SUCCESS = Response(200)
NOT_ENOUGH_ARGS = Response(400, message='Not enough arguments')
ITEM_ALREADY_EXISTS = Response(409, message='Item already exists')
NOT_FOUND = Response(404, message='Item not found')
UNAUTHORIZED = Response(401, message='Wrong password or email')
INVALID_ACCESS_TOKEN = Response(401, message='Access token does not exist or expired. '
                                             'Please, get the new access token via refresh token')
INVALID_REFRESH_TOKEN = Response(401, message='Refresh token does not exist or expired. '
                                              'Please, authenticate again')
INVALID_PARAMETER = Response(400, message='One or more parameters are invalid')
