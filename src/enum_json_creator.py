import json
import os.path
import sys
from enum import Enum
from typing import List, Type

import entities
from utils import file_util


def enum_to_api_representation_dict(api_representables: List[Type[entities.ApiRepresentable]]) -> str:
    representations = []
    for api_representable in api_representables:
        representations += [api_representable.to_api_representation()]
    # mypy does not recognize that json_util.to_json_str returns a str.
    # Hence the useless str()
    return str(json.dumps(representations, separators=(',', ':')))


def write_enum_as_api_representation_to_file(base_dir: str, filename: str, enum_type: Type[Enum]) -> None:
    file_util.write(os.path.join(base_dir, filename), enum_to_api_representation_dict(list(enum_type)))


if __name__ == "__main__":
    base_directory = "dist/enums"
    if len(sys.argv) > 1:
        base_directory = sys.argv[1]
    if not os.path.exists(base_directory):
        raise FileNotFoundError(f"There is no such directory '{base_directory}'.")
    enum_types = {entities.Canteen: "canteens.json", entities.Label: "labels.json", entities.Language: "languages.json"}
    for key, value in enum_types.items():
        write_enum_as_api_representation_to_file(base_directory, value, key)
