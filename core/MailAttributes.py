from enum import Enum

from core.Mail import Mail


# TODO add Callable as type
class MailAttributes(Enum):
    # TODO attachments, fix subject
    SUBJECT = Mail.get_subject
    BODY = Mail.get_raw_text
