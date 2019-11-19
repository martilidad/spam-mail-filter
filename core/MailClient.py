from abc import abstractmethod
from email.message import Message


class MailClient:
    @abstractmethod
    def __init__(self, host: str, port: int):
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
    def get_all_uids(self) -> [bytes]:
        pass

    @abstractmethod
    def get_mail_for_uid(self, uid: bytes) -> Message:
        pass

    @abstractmethod
    def get_raw_mail_for_uid(self, uid: bytes) -> str:
        pass

    @abstractmethod
    def move_mail(self, uid: bytes, destination: str):
        pass

    @abstractmethod
    def flag_mail(self, uid: bytes):
        pass
