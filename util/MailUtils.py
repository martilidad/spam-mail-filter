from core.Mail import Mail


def mails_to_strings(mails: [Mail]):
    return [mail.raw_text for mail in mails]


def strings_to_mails(strings: [str]) -> [Mail]:
    return [Mail(string) for string in strings]

