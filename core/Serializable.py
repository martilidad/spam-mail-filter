from abc import abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')


class Serializable(Generic[T]):
    @property
    @abstractmethod
    def save_folder(self):
        pass

    @abstractmethod
    def serialize(self):
        pass

    @staticmethod
    @abstractmethod
    def deserialize() -> T:
        pass
