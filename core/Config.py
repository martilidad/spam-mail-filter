import os
from configparser import ConfigParser


class Config:
    def __init__(self):
        parser = ConfigParser()
        path = os.path.dirname(__file__) + "/../spamfilter.ini"
        parser.read(path)

        mail_config = parser['mail']
        self.username = mail_config.get('username', '')
        self.password = mail_config.get('password', '')
        self.host = mail_config.get('host', 'localhost')
        self.port = mail_config.getint('port', 993)

        spam_config = parser['spam']
        self.check_interval = spam_config.getfloat('check_interval', 15)
        self.score_threshold = spam_config.getfloat('score_threshold', 0.5)

        file_config = parser['file']
        self.trackfile = file_config.get('trackfile_name', 'trackfile.trc')

        folder_config = parser['folder']
        self.inbox = folder_config.get('inbox', 'INBOX')
        self.spam_folder = folder_config.get('spam_folder')

        process_config = parser['process']
        self.dryrun = process_config.getboolean('dryrun', False)
