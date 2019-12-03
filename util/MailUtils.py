from email.message import Message
from typing import List

from core.Mail import Mail


def mails_to_strings(mails: List[Mail]):
    return [str(mail) for mail in mails]


def strings_to_mails(strings: List[str]) -> List[Mail]:
    return [string_to_mail(string) for string in strings]


def string_to_mail(string) -> Mail:
    if type(string) is bytes:
        return Mail(string.decode('UTF-8', errors='replace'), '', '')
    return Mail(string, '', '')


def messages_to_mails(messages: List[Message]) -> List[Mail]:
    return [message_to_mail(message) for message in messages]


def message_to_mail(message):
    raw_text = unwrap_payload(message)
    subject = opt_header_to_str(message, 'Subject')
    sender = opt_header_to_str(message, 'from')
    return Mail(raw_text, subject, sender)


def opt_header_to_str(message: Message, header) -> str:
    results = message.get_all(header)
    if len(results) > 0:
        return str(results[0])
    return ''


def unwrap_payload(message: Message) -> str:
    if message.is_multipart():
        parts = message.get_payload()
        res = ""
        for part in parts:
            res += unwrap_payload(part)
            res += "\n\n"
        return res
    else:
        payload = message.get_payload(decode=True)
        if type(payload) is bytes:
            payload = payload.decode(errors='replace')
        return payload
