from imap.ImapClient import ImapClient
from util import MailUtils

from bayes.BayesClassifier import BayesClassifier
from core.EnronDataset import EnronDataset
from sklearn.model_selection import train_test_split

import threading


class SpamFilter:

    def __init__(self):
        # TODO read values from config file
        username = ''
        password = ''
        host = ''

        # init imapClient with host
        self.imap = ImapClient(host)
        self.imap.login(username, password)

        # do trainig
        data = EnronDataset().load_files()
        train_texts, _, train_labels, _ = train_test_split(
            data.data, data.target, train_size=0.6)
        train_mails = MailUtils.strings_to_mails(train_texts)
        self.classifier = BayesClassifier(train_mails, train_labels)
        self.classifier.train()

        self.mailChecker = self.MailCheckerThread(15 * 60, self.imap, self.classifier)
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
            self.__mail_check()
            while not self.stopped.wait(self.interval):
                self.__mail_check()

        def __mail_check(self):
            print("checking mails")
            uids = self.imap.get_all_uids()
            for uid in uids:
                # TODO check if uid is new
                mail = self.imap.get_mail_for_uid(uid)
                score = self.classifier.classify(MailUtils.message_to_mails(mail))
                if score[0] > 0.5:
                    print("spam detected")
                    self.imap.move_mail(uid, "[Gmail]/Spam")

        def stop(self):
            self.stopped.set()
            self.join()
