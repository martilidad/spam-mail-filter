import json
import os
from typing import TypeVar, Optional, List, Dict

DATA_DIR = os.path.dirname(__file__) + "\..\data\\"

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


def add_uids_to_trackfile(trackfile: str, trained_uids: Dict[str, List[int]]):
    tracked_uids = deserialize(trackfile)
    if tracked_uids is None:
        tracked_uids = {}
    elif type(tracked_uids) is not dict:
        tracked_uids = {}

    keys = set(tracked_uids).union(trained_uids)
    no = []
    merged = dict(
        (k, list(set(tracked_uids.get(k, no) + trained_uids.get(k, no))))
        for k in keys)
    for value in merged.values():
        value.sort()

    serialize(merged, trackfile)


def clear_trackfile(trackfile: str):
    serialize({}, trackfile)
