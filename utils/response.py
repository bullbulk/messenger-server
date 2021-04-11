import json


class Response:
    def __init__(self, status_code: int, **kwargs):
        self.status_code = status_code
        self.dict = {
            'status_code': status_code,
            'success': status_code == 200,
            **kwargs
        }

    def __setitem__(self, key, value):
        self.dict[key] = value

    def json(self):
        return json.dumps(self.dict), self.status_code

    def copy(self):
        return self.__class__(**self.dict)
