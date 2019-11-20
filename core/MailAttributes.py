from enum import Enum, auto
from typing import Callable

from core.Mail import Mail


# TODO add Callable as type
class MailAttributes(Enum):
    # TODO attachments, fix subject
    SUBJECT = Mail.get_raw_text
    BODY = Mail.get_raw_text

