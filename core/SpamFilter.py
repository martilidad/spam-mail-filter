from imap.ImapClient import ImapClient
from util import MailUtils
from core.MailChecker import MailChecker

from bayes.BayesClassifier import BayesClassifier
from core.EnronDataset import EnronDataset
from sklearn.model_selection import train_test_split


class SpamFilter:
    def __init__(self):
        # TODO read values from config file
        self.username = ''
        self.password = ''
        host = ''

        # init imapClient with host
        self.imap = ImapClient(host)

        # do trainig
        data = EnronDataset().load_files()
        train_texts, _, train_labels, _ = train_test_split(data.data,
                                                           data.target,
                                                           train_size=0.6)
        train_mails = MailUtils.strings_to_mails(train_texts)
        self.classifier = BayesClassifier(train_mails, train_labels)
        self.classifier.train()

        self.mailChecker = MailChecker(15 * 60, self.imap, self.classifier)

    def start(self):
        self.imap.login(self.username, self.password)
        self.mailChecker.start()

    def stop(self):
        self.mailChecker.stop()
        self.imap.logout()
