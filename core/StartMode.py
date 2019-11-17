from enum import Enum, auto


class StartMode(Enum):
    """
    training: loads selected dataset from raw data and trains the base network
    pretrained: loads a previously serialized network from disk
    no_training: does not train the network before checking for mails
    usermail_training: trains the network from train_ham_mailbox and train_spam_mailbox
    """
    TRAINING = auto()
    PRETRAINED = auto()
    NO_TRAINING = auto()
    USERMAIL_TRAINING = auto()
