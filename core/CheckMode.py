from enum import Enum, auto


class CheckMode(Enum):
    """
    none: does not check for mails, immediately terminates the application after full startup
    normal: checks mails and moves them corresponding depending on spam score
    dryrun: checks mails but does not move them, logs found mails and updates trackfile
    """
    NONE = auto()
    NORMAL = auto()
    DRYRUN = auto()
