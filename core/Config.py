import datetime
import logging
import os
from argparse import ArgumentParser
from configparser import ConfigParser

from classification.ClassificationConfig import ClassificationConfig
from core.CheckMode import CheckMode
from core.StartMode import StartMode


class ConfigSection:

    def __init__(self, name: str, argParser, configParser):
        self.argParser = argParser
        self.arg_group = argParser.add_argument_group(name)
        self.config_group = configParser[name]

    def parse(self, name, default=None, type: type = str, description=None):
        value = default
        if type is str:
            value = self.config_group.get(name, default)
        elif type is int:
            value = self.config_group.getint(name, default)
        elif type is bool:
            value = self.config_group.getboolean(name, default)
        elif type is float:
            value = self.config_group.getfloat(name, default)
        elif callable(type):
            # type is a custom parsing function/lambda
            value = type(self.config_group.get(name, default))
        else:
            raise ValueError('unkown config-key type' + str(type))
        self.arg_group.add_argument('--' + name, type=type, default=value, help=description)
        # return default value for now might get updated later
        return value


class Config:
    def __init__(self):
        configParser = ConfigParser()
        argParser = ArgumentParser()
        path = os.path.dirname(__file__) + "/../spamfilter.ini"
        configParser.read(path)

        mail_config = ConfigSection('mail', argParser, configParser)
        self.username = mail_config.parse('username', '')
        self.password = mail_config.parse('password', '')
        self.host = mail_config.parse('host', 'localhost')
        self.port = mail_config.parse('port', 993, int)

        spam_config = ConfigSection('spam', argParser, configParser)
        self.check_interval = spam_config.parse('check_interval', 15, float)
        self.score_threshold = spam_config.parse('score_threshold', 0.5, float)

        file_config = ConfigSection('file', argParser, configParser)
        self.trackfile = file_config.parse('trackfile_name', 'trackfile.trc')

        folder_config = ConfigSection('folder', argParser, configParser)
        self.inbox = folder_config.parse('inbox', 'INBOX')
        self.spam_folder = folder_config.parse('spam_folder')
        self.train_ham_mailbox = folder_config.parse('train_ham_mailbox')
        self.train_spam_mailbox = folder_config.parse('train_spam_mailbox')

        external_config = ConfigSection('external', argParser, configParser)
        self.google_api_token = external_config.parse('google_api_token')

        self.classification_config = ClassificationConfig(
            ConfigSection('classification', argParser, configParser), self)

        process_config = ConfigSection('process', argParser, configParser)
        self.console_log_level = process_config.parse(
            'console_log_level', 'INFO', type=lambda x: logging._nameToLevel[x])
        self.create_logfiles = process_config.parse('create_logfiles', 'False', bool)
        self.start_mode = process_config.parse('start_mode',
                                               'training', type=lambda x: StartMode[x])
        self.check_mode = process_config.parse('check_mode', 'normal', type=lambda x: CheckMode[x])
        self.dryrun = process_config.parse('dryrun', False, bool)
        self.usermail_training = process_config.parse(
            'usermail_training', False, bool)
        self.track_train_mails = process_config.parse('track_train_mails', True, bool)
        self.max_train_mails = process_config.parse('max_train_mails', 500, int)
        self.batch_size = process_config.parse('batch_size', 100, int)
        self.__dict__.update(argParser.parse_args().__dict__)
        self.configure_logging()

    def configure_logging(self):
        if self.create_logfiles:
            logdir = os.path.dirname(__file__) + "/../log/"
            os.makedirs(logdir, exist_ok=True)
            filename = datetime.datetime.now().replace(
                microsecond=0).isoformat().replace(':', '-') + ".log"
            logfile = logdir + "spamfilter_" + filename
            logging.basicConfig(
                level=logging.DEBUG,
                filename=logfile,
                filemode='w',
                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt='%y-%m-%d %H:%M',
            )
        console = logging.StreamHandler()
        console.setLevel(self.console_log_level)
        console.setFormatter(
            logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
        logging.getLogger('').addHandler(console)
