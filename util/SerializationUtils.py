import json
import os
from typing import TypeVar, Optional

DATA_DIR = os.path.dirname(__file__) + "/../data/"

T = TypeVar('T')


def get_absolute_file_path(filename):
    filename = os.path.normpath(filename)
    return DATA_DIR + filename


def serialize(obj: object, filename: str):
    file = get_absolute_file_path(filename)
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))

    with open(file, 'w+') as wfile:
        json.dump(obj, wfile)


def deserialize(filename: str) -> Optional[object]:
    file = get_absolute_file_path(filename)
    try:
        with open(file, 'r') as rfile:
            obj = json.load(rfile)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return None
    return obj
