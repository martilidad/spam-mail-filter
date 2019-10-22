import imaplib  # https://docs.python.org/3/library/imaplib.html
import email  # https://docs.python.org/3/library/email.html
# https://www.youtube.com/watch?v=bbPwv0TP2UQ
# https://github.com/isbg/isbg
# https://tools.ietf.org/html/rfc3501


def __do_auth():
    # do authentication
    # https://www.google.com/settings/security/lesssecureapps
    # put data into separate file
    username = ''
    password = ''

    conn = imaplib.IMAP4_SSL('')
    conn.login(username, password)

    return conn


def __retrieve_mails(conn):
    # retrieve unseen mails
    conn.list()
    conn.select('INBOX')
    # Recent or unseen or do i have to store the ids of the mails?
    conn.recent()  # only first client will receive the mail
    uids = conn.search(None, '(UNSEEN)')  # what is with SEEN mails on other clients

    mails = []
    for uid in uids:
        res = conn.uid("FETCH", uid, "(BODY.PEEK[])")
        body = res[1][0][1]
        if isinstance(body, bytes):
            mail = email.message_from_bytes(body)
            mails.append(mail)
        else:
            mail = email.message_from_string(body)
            mails.append(mail)
            # unwrap if it is multipart mail

    return mails


def __process_mail(conn, msg_uid):
    result = conn.uid('COPY', msg_uid, '<destination folder>')

    if result[0] == 'OK':
        conn.uid('STORE', msg_uid, '+FLAGS', '(\Deleted)')
        conn.expunge()


def __shutdown(conn):
    conn.logout()


conn = __do_auth()
__retrieve_mails(conn)
# foreach mail # or retrieve only uids of unseen and then iterate over uids and retrieve mail step by step
    # calculate spam score
    # do something if score is higher than certain value
__shutdown(conn)

# Exception handling. finally shutdown
