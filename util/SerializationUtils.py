import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "/../data/")


def __get_absolute_file_path(filename):
    filename = os.path.normpath(filename)
    return os.path.join(DATA_DIR, filename)


def serialize(obj, filename: str):
    file = __get_absolute_file_path(filename)
    with open(file, 'w+') as wfile:
        json.dump(obj, wfile)


def deserialize(filename: str):
    file = __get_absolute_file_path(filename)
    try:
        with open(file, 'r') as rfile:
            obj = json.load(rfile)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return None
    return obj
