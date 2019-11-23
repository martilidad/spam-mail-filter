from abc import abstractmethod
from typing import TypeVar, Generic

from util import SerializationUtils

T = TypeVar('T')


class Serializable(Generic[T]):
    @property
    @abstractmethod
    def save_folder(self):
        pass

    def resolve_folder(self, sub_folder: str = None):
        base_folder: str
        if sub_folder is not None:
            base_folder = sub_folder + self.save_folder
        else:
            base_folder = SerializationUtils.get_absolute_file_path(
                self.save_folder) + "/"
        return base_folder

    @abstractmethod
    def serialize(self, sub_folder: str = None):
        pass

    @abstractmethod
    def deserialize(self, sub_folder: str = None) -> T:
        pass
