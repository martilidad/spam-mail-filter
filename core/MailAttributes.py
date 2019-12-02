from enum import Enum
from functools import partial

from core.Mail import Mail


# TODO add Callable as type
class MailAttributes(Enum):
    SUBJECT = partial(Mail.get_subject)
    BODY = partial(Mail.get_raw_text)
    FROM = partial(Mail.get_from)

    def __call__(self, *args):
        return self.value(*args)
