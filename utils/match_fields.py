from typing import List, Dict, Union


def match_required_fields(fields: Union[Dict, List], required_fields: List):
    fields = fields if isinstance(fields, list) else fields.keys()
    for i in required_fields:
        if i not in fields:
            return False
    return True
