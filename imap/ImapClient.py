import imaplib  # https://docs.python.org/3/library/imaplib.html
import email  # https://docs.python.org/3/library/email.html
from core.MailClient import MailClient


class ImapClient(MailClient):
    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self.conn = imaplib.IMAP4_SSL(host, port)

    def login(self, user: str, password: str):
        self.conn.login(user, password)

    def logout(self):
        self.conn.logout()

    def select_mailbox(self, mailbox: str):
        self.conn.select(mailbox)

    def get_all_uids(self) -> [bytes]:
        result, uids = self.conn.uid('SEARCH', None, 'All')
        return uids[0].split()

    def get_mail_for_uid(self, uid: bytes) -> email.message.Message:
        result, data = self.conn.uid('FETCH', uid, '(RFC822)')
        body = data[0][1]
        if isinstance(body, bytes):
            mail = email.message_from_bytes(body)
        else:
            mail = email.message_from_string(body)
        return mail

    def get_raw_mail_for_uid(self, uid: bytes) -> str:
        result, data = self.conn.uid('FETCH', uid, '(RFC822)')
        body = data[0][1]
        if isinstance(body, bytes):
            mail = body.decode()
        else:
            mail = body
        return mail

    def move_mail(self, uid: bytes, destination: str):
        result = self.conn.uid('COPY', uid, destination)

        if result[0] == 'OK':
            self.conn.uid('STORE', uid, '+FLAGS', '(\Deleted)')
            self.conn.expunge()
