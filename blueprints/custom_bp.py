from flask import Blueprint


class CustomBlueprint(Blueprint):
    data = []

    def set_data(self, data: dict):
        for k, v in data.items():
            self.__dict__[k] = v
