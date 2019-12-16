import email  # https://docs.python.org/3/library/email.html
import imaplib  # https://docs.python.org/3/library/imaplib.html
import logging
import re
import socket
from typing import List, Tuple

from core.mail.MailClient import MailClient
from imap.ImapException import ImapException
from util import SerializationUtils


class ImapClient(MailClient):
    def __init__(self, host: str, port: int, ssl: bool):
        super().__init__(host, port, ssl)
        socket.setdefaulttimeout(2)
        try:
            if ssl:
                self.conn = imaplib.IMAP4_SSL(host, port)
            else:
                self.conn = imaplib.IMAP4(host, port)
        except socket.error as ex:
            logging.fatal('Could not connect to host ' + host + ':' + str(port))
            raise ImapException(ex)

    def login(self, user: str, password: str):
        try:
            self.conn.login(user, password)
        except imaplib.IMAP4.error as ex:
            logging.fatal('Unable to authenticate')
            raise ImapException(ex)

    def logout(self):
        self.conn.logout()

    def select_mailbox(self, mailbox: str):
        status, _ = self.conn.select(mailbox)
        if status != 'OK':
            logging.fatal('Unable to select mailbox: ' + mailbox)
            self.print_valid_folders()
            self.logout()
            raise ImapException('Unable to select mailbox: ' + mailbox)

    def print_valid_folders(self):
        status, lst = self.conn.list()
        if status == 'OK':
            print("Valid folders:")
            for response in lst:
                if response.find(b'Noselect') == -1:
                    decoded = response.decode()
                    # everything after the first forward slash should be The correct Folder Name
                    folder: str = decoded[decoded.find('/') + 1:]
                    print(folder.strip(' \'\"'))
        else:
            raise ImapException('Unable to list valid mailboxes')

    def get_mailbox_identifier(self, mailbox: str):
        status, response = self.conn.status(mailbox, '(UIDVALIDITY)')
        if status == 'OK':
            body = response[0].decode()
            match = re.search('UIDVALIDITY ([0-9]+)', body)
            if match is not None:
                uidvalidity = int(match.groups()[0])
            else:
                uidvalidity = 0

            return uidvalidity
        else:
            return 0

    def get_all_uids(self) -> List[bytes]:
        _, uids = self.conn.uid('SEARCH', None, 'All')
        return uids[0].split()

    def get_new_uids(self, mailbox: str, trackfile: str) -> Tuple[List[bytes], str]:
        mbid = str(self.get_mailbox_identifier(mailbox))
        uids = self.get_all_uids()
        tracked_uids = SerializationUtils.deserialize(trackfile)
        if tracked_uids is None:
            tracked_uids = {}
        elif type(tracked_uids) is not dict:
            tracked_uids = {}

        new_uids = [
            u for u in uids if int(u) not in tracked_uids.get(mbid, [])
        ]
        return new_uids, mbid

    def get_mails_for_uids(self,
                           uids: List[bytes]) -> List[email.message.Message]:
        comma_separated_uids = ','.join([uid.decode() for uid in uids])
        _, data = self.conn.uid('FETCH', comma_separated_uids, '(RFC822)')
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
        status, result = self.conn.uid('COPY', uid, destination)

        if status == 'OK':
            self.conn.uid('STORE', uid, '+FLAGS', '(\Deleted)')
            self.conn.expunge()
        else:
            logging.info('Could not copy mail to destination folder: ' + destination +
                         '; you probably provided an invalid mailbox as spam_folder')

    def flag_mail(self, uid: bytes):
        self.conn.uid('STORE', uid, '+FLAGS', '(\Flagged)')
