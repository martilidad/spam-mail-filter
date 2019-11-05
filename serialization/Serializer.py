import json
import os


class Serializer:
    def __init__(self):
        super().__init__()
        self.data_dir = os.path.dirname(__file__) + "/../data/"

    def __get_absolute_file_path(self, filename):
        filename = filename.strip()
        if filename.startswith('/'):
            filename = filename[1:]
        return self.data_dir + filename

    def serialize(self, obj, filename: str):
        file = self.__get_absolute_file_path(filename)
        with open(file, 'w+') as wfile:
            json.dump(obj, wfile)

    def deserialize(self, filename: str):
        file = self.__get_absolute_file_path(filename)
        try:
            with open(file, 'r') as rfile:
                obj = json.load(rfile)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return None
        return obj
