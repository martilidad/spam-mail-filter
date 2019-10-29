from core.Mail import Mail
from email import message


def mails_to_strings(mails: [Mail]):
    return [mail.raw_text for mail in mails]


def strings_to_mails(strings: [str]) -> [Mail]:
    return [Mail(string) for string in strings]


def message_to_mails(mail: message) -> [Mail]:
    return [Mail(mail.as_string())]
