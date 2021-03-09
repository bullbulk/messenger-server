from typing import List, Dict, Union


def match_required_params(params: Union[Dict, List], required_params: List):
    print(params, required_params)
    params = params if isinstance(params, list) else params.keys()
    for i in required_params:
        if i not in params:
            return False
    return True
