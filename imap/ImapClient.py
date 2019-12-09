import email  # https://docs.python.org/3/library/email.html
import imaplib  # https://docs.python.org/3/library/imaplib.html
import logging
import re
from typing import List

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
        status, _ = self.conn.select(mailbox)
        if status != 'OK':
            logging.fatal('Unable to select mailbox: ' + mailbox)
            self.print_valid_folders()
            exit(-1)

    def print_valid_folders(self):
        list: List[bytes]
        status, list = self.conn.list()
        print("Valid folders:")
        for response in list:
            if response.find(b'Noselect') == -1:
                folder = response.split(b'"')[-2].decode()
                print(folder)

    def get_mailbox_identifier(self, mailbox: str):
        _, response = self.conn.status(mailbox, '(UIDVALIDITY)')
        body = response[0].decode()
        match = re.search('UIDVALIDITY ([0-9]+)', body)
        if match is not None:
            uidvalidity = int(match.groups()[0])
        else:
            uidvalidity = 0

        return uidvalidity

    def get_all_uids(self) -> List[bytes]:
        result, uids = self.conn.uid('SEARCH', None, 'All')
        return uids[0].split()

    def get_mails_for_uids(self,
                           uids: List[bytes]) -> List[email.message.Message]:
        comma_separated_uids = ','.join([uid.decode() for uid in uids])
        result, data = self.conn.uid('FETCH', comma_separated_uids, '(RFC822)')
        mails: List[email.message.Message] = []
        if data[0] is None:
            return mails

        for i in range(int(len(data) / 2)):
            body = data[i * 2][1]
            if isinstance(body, bytes):
                mail = email.message_from_bytes(body)
            else:
                mail = email.message_from_string(body)
            mails.append(mail)
        return mails

    def move_mail(self, uid: bytes, destination: str):
        result = self.conn.uid('COPY', uid, destination)

        if result[0] == 'OK':
            self.conn.uid('STORE', uid, '+FLAGS', '(\Deleted)')
            self.conn.expunge()

    def flag_mail(self, uid: bytes):
        self.conn.uid('STORE', uid, '+FLAGS', '(\Flagged)')
