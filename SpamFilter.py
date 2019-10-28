from imap.ImapClient import ImapClient
from bayes.BayesClassifier import  BayesClassifier
import threading


class SpamFilter:

    def __init__(self):
        # read config values
        username = ''
        password = ''
        host = 'imap.gmail.com'

        # init imapClient with host
        self.imap = ImapClient(host)
        self.imap.login(username, password)

        # do trainig
        self.classifier = BayesClassifier(None, None)

        self.mailChecker = self.MailCheckerThread(15 * 60, self.imap)
        self.mailChecker.start()

    def stop(self):
        self.mailChecker.stop()
        self.imap.logout()

    class MailCheckerThread(threading.Thread):

        def __init__(self, interval, imap, classifier):
            threading.Thread.__init__(self)
            self.stopped = threading.Event()
            self.interval = interval
            self.imap = imap
            self.classifier = classifier

        def run(self):
            while not self.stopped.wait(self.interval):
                self.__mail_check()

        def __mail_check(self):
            uids = self.imap.get_all_uids()
            for uid in uids:
                # uid überprüfen
                mail = self.imap.get_mail_for_uid(uid)
                score = self.classifier.classify(mail)
                if score > 0.5:
                    self.imap.move_mail(uid, "spam")

        def stop(self):
            self.stopped.set()
            self.join()
