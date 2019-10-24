import imaplib  # https://docs.python.org/3/library/imaplib.html
import email  # https://docs.python.org/3/library/email.html


def __do_auth():
    # https://www.google.com/settings/security/lesssecureapps
    username = ''
    password = ''

    conn = imaplib.IMAP4_SSL('imap.gmail.com')  # imap.gmail.com / imap.gmx.net
    conn.login(username, password)

    return conn


def __retrieve_new_uids(conn):
    conn.select('INBOX')
    # only first client will receive the mail, should be replaced with a list of already scanned mails
    result, uids = conn.uid('SEARCH', None, 'All')  # conn.recent()
    if result != 'OK':
        uids = []
    return uids[0].split()


def __retrieve_mail(conn, uid):
    result, data = conn.uid('FETCH', uid, '(BODY.PEEK[])')
    body = data[0][1]
    if isinstance(body, bytes):
        mail = email.message_from_bytes(body)
    else:
        mail = email.message_from_string(body)
    # unwrap if it is multipart mail

    return mail


def __process_mail_as_spam(conn, msg_uid):
    result = conn.uid('COPY', msg_uid, '[Gmail]/Spam')

    if result[0] == 'OK':
        conn.uid('STORE', msg_uid, '+FLAGS', '(\Deleted)')
        conn.expunge()


def __process_mail(mail):
    payload = mail.get_payload()
    subject = mail['Subject']
    sender = mail['From']
    to = mail['To']


def __shutdown(conn):
    conn.logout()


if __name__ == "__main__":
    conn = __do_auth()
    uids = __retrieve_new_uids(conn)
    for uid in uids:
        mail = __retrieve_mail(conn, uid)
        __process_mail(mail)
        score = 0  # calculate spam score
        if score > 0.5:
            __process_mail_as_spam(conn, uid)
    __shutdown(conn)
