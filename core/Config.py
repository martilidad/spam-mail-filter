import datetime
import logging
import os
from argparse import ArgumentParser
from configparser import ConfigParser

from classification.ClassificationConfig import ClassificationConfig
from core.CheckMode import CheckMode
from util.MetaContainer import MetaContainer
from core.StartMode import StartMode


class ConfigSection:
    def __init__(self, name: str, arg_parser, config_parser, *args, **kwargs):
        self.argParser = arg_parser
        self.arg_group = arg_parser.add_argument_group(name, *args, **kwargs)
        self.config_group = config_parser[name]

    def parse(self, name, default=None, type: type = str, description=None):
        value = default
        if type is str:
            value = self.config_group.get(name, default)
        elif type is int:
            value = self.config_group.getint(name, default)
        elif type is bool:
            value = self.config_group.getboolean(name, default)
            # arparser normally would pass x to bool(x) this results in confusing behaviour
            type = lambda x: x.lower() not in ("no", "false", "f", "0")
        elif type is float:
            value = self.config_group.getfloat(name, default)
        elif callable(type):
            # type is a custom parsing function/lambda
            value = type(self.config_group.get(name, default))
        else:
            raise ValueError('unkown config-key type' + str(type))
        self.arg_group.add_argument('--' + name,
                                    type=type,
                                    default=value,
                                    help=description)
        # return default/config value for now. might get updated later
        return value


class Config(MetaContainer):
    def __init__(self):
        config_parser = ConfigParser()
        arg_parser = ArgumentParser()
        path = os.path.dirname(__file__) + "/../spamfilter.ini"
        config_parser.read(path)

        mail_config = ConfigSection('mail', arg_parser, config_parser)
        self.username = mail_config.parse('username', '')
        self.password = mail_config.parse('password', '')
        self.host = mail_config.parse('host', 'localhost')
        self.port = mail_config.parse('port', 993, int)
        self.ssl = mail_config.parse('ssl', True, bool)

        spam_config = ConfigSection('spam', arg_parser, config_parser)
        self.check_interval = spam_config.parse('check_interval', 15, float)
        self.score_threshold = spam_config.parse('score_threshold', 0.5, float)

        file_config = ConfigSection('file', arg_parser, config_parser)
        self.trackfile = file_config.parse('trackfile_name', 'trackfile.trc')

        folder_config = ConfigSection(
            'folder', arg_parser, config_parser,
            'Valid folders can be displayed with --start_mode LIST_MAIL_FOLDERS'
        )
        self.inbox = folder_config.parse('inbox', 'INBOX')
        self.spam_folder = folder_config.parse('spam_folder')
        self.train_ham_mailbox = folder_config.parse('train_ham_mailbox')
        self.train_spam_mailbox = folder_config.parse('train_spam_mailbox')

        external_config = ConfigSection('external', arg_parser, config_parser)
        self.google_api_token = external_config.parse('google_api_token')

        self.classification_config = ClassificationConfig(
            ConfigSection(
                'classification',
                arg_parser,
                config_parser,
                description=
                'Sum of weights must be > 1. Classifiers with weight 0 will not be initialized'
            ), self)

        process_config = ConfigSection('process', arg_parser, config_parser)
        self.console_log_level = process_config.parse(
            'console_log_level',
            'INFO',
            type=lambda x: logging._nameToLevel[x],
            description=self.list_to_help(logging._nameToLevel.keys()))
        self.create_logfiles = process_config.parse('create_logfiles', 'False',
                                                    bool)
        self.start_mode = process_config.parse(
            'start_mode',
            'training',
            type=lambda x: StartMode[x],
            description=self.enum_to_help(StartMode))
        self.check_mode = process_config.parse(
            'check_mode',
            'normal',
            type=lambda x: CheckMode[x],
            description=self.enum_to_help(CheckMode))
        self.track_train_mails = process_config.parse('track_train_mails',
                                                      True, bool)
        self.max_train_mails = process_config.parse('max_train_mails', 500,
                                                    int)
        self.batch_size = process_config.parse('batch_size', 100, int)

        self.__dict__.update(arg_parser.parse_args().__dict__)
        # has to be done after parse_args()
        self.configure_logging()

    @staticmethod
    def list_to_help(list):
        result = 'Valid Values: '
        for item in list:
            result += str(item) + ' '
        return result

    @staticmethod
    def enum_to_help(enum):
        return Config.list_to_help([val.name for val in list(enum)])

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
