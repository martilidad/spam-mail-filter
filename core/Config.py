import os
from configparser import ConfigParser

from classification.ClassificationConfig import ClassificationConfig
from core.CheckMode import CheckMode
from core.StartMode import StartMode


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
        self.train_ham_mailbox = folder_config.get('train_ham_mailbox')
        self.train_spam_mailbox = folder_config.get('train_spam_mailbox')

        self.classification_config = ClassificationConfig(
            parser['classification'])

        process_config = parser['process']
        self.start_mode = StartMode[process_config.get('start_mode',
                                                       'training')]
        self.check_mode = CheckMode[process_config.get('check_mode', 'normal')]
        self.dryrun = process_config.getboolean('dryrun', False)
        self.usermail_training = process_config.getboolean(
            'usermail_training', False)
        self.max_train_mails = process_config.getint('max_train_mails', 500)
