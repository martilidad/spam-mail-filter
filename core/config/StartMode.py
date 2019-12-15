from enum import Enum, auto


class StartMode(Enum):
    """
    pretrained: loads a previously serialized network from disk
    usermail_training: trains the network from train_ham_mailbox and train_spam_mailbox
    online_training: combination of pretrained and usermail training: loads a serialized classifier and applies
                    usermail training as online training
    testdata_training: loads selected dataset from raw data and trains the base network
    no_training: does not train the network before checking for mails
    list_mail_folders: only prints out imap folders
    """
    PRETRAINED = auto()
    USERMAIL_TRAINING = auto()
    ONLINE_TRAINING = auto()
    TESTDATA_TRAINING = auto()
    NO_TRAINING = auto()
    LIST_MAIL_FOLDERS = auto()
