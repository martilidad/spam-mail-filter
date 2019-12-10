from abc import abstractmethod
from email.message import Message
from typing import List


class MailClient:
    @abstractmethod
    def __init__(self, host: str, port: int, ssl: bool):
        pass

    @abstractmethod
    def login(self, user: str, password: str):
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def select_mailbox(self, mailbox: str):
        pass

    @abstractmethod
    def print_valid_folders(self):
        pass

    @abstractmethod
    def get_mailbox_identifier(self, mailbox: str) -> int:
        pass

    @abstractmethod
    def get_all_uids(self) -> List[bytes]:
        pass

    @abstractmethod
    def get_mails_for_uids(self, uids: List[bytes]) -> List[Message]:
        pass

    @abstractmethod
    def move_mail(self, uid: bytes, destination: str):
        pass

    @abstractmethod
    def flag_mail(self, uid: bytes):
        pass
