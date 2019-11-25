from email.message import Message

from core.Mail import Mail


def mails_to_strings(mails: [Mail]):
    return [str(mail) for mail in mails]


def strings_to_mails(strings: [str]) -> [Mail]:
    return [string_to_mail(string) for string in strings]


def string_to_mail(string) -> Mail:
    if type(string) is bytes:
        return Mail(string.decode('UTF-8', errors='replace'), '')
    return Mail(string, '')


def messages_to_mails(messages: [Message]) -> [Mail]:
    return [message_to_mail(message) for message in messages]


def message_to_mail(message):
    raw_text = select_payload(message)
    if type(raw_text) is bytes:
        raw_text = raw_text.decode('UTF-8', errors='replace')
    subject = opt_header_to_str(message, 'Subject')
    return Mail(raw_text, subject)


def opt_header_to_str(message: Message, header) -> str:
    results = message.get_all(header)
    if len(results) > 0:
        return str(results[0])
    return ''


def payload_list(message) -> [Message]:
    """
    This function unwraps all message parts for multipart mails into one list of messages
    :param message:
    :return: message list. with flattened hierarchy
    """
    payloads = message.get_payload()
    if type(payloads) is list:
        result = []
        for payload in payloads:
            otherList = payload_list(payload)
            result = [*result, *otherList]
        return result
    else:
        return [message]


def select_payload(message: Message) -> str:
    if type(message.get_payload()) is list:
        messages = payload_list(message)
        for msg in messages:
            if msg.get_content_type() == "text/plain":
                return msg.get_payload(decode=True)
        for msg in messages:
            if msg.get_content_type() == "text/html":
                return msg.get_payload(decode=True)
        return messages[0].get_payload(decode=True)
    return message.get_payload(decode=True)
