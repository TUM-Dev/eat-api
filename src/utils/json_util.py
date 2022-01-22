import json
from enum import Enum
from json import JSONEncoder
from typing import Any, Dict, Union


class CustomJsonEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o.__class__, "to_json_obj"):
            return o.to_json_obj()
        return super().default(o)


def order_json_objects(obj):
    """
    Recusively orders all elemts in a Json object.
    Source:
    https://stackoverflow.com/questions/25851183/how-to-compare-two-json-objects-with-the-same-elements-in-a-different-order-equa
    """
    if isinstance(obj, dict):
        return sorted((k, order_json_objects(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(order_json_objects(x) for x in obj)
    return obj


def dict_to_json_dict(dict_: Dict[Any, Any]) -> Dict[Union[str, float, int], Any]:
    json_dict = {}
    for key, value in dict_.items():
        if type(key) in [int, float]:
            json_key = key
        elif isinstance(key, Enum):
            json_key = key.name
        else:
            json_key = str(key)
        if hasattr(value.__class__, "to_json_obj"):
            json_value = value.to_json_obj
        else:
            json_value = value
        json_dict[json_key] = json_value
    return json_dict


def to_json_str(obj: Any) -> str:
    return json.dumps(obj, cls=CustomJsonEncoder, separators=(",", ":"))
