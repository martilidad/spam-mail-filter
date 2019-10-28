import imaplib


class ImapClient:

    def __init__(self, host):
        self.conn = imaplib.IMAP4_SSL(host)

    def login(self, user, password):
        self.conn.login(user, password)

    def logout(self):
        self.conn.logout()

    def get_all_uids(self):
        pass

    def get_mail_for_uid(self, uid):
        pass

    def move_mail(self, uid, destination):
        pass
