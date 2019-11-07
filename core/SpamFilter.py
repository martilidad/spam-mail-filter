from sklearn.model_selection import train_test_split

from bayes.BayesClassifier import BayesClassifier
from core.Config import Config
from core.EnronDataset import EnronDataset
from core.MailChecker import MailChecker
from imap.ImapClient import ImapClient
from util import MailUtils


class SpamFilter:
    def __init__(self):
        self.config = Config()

        # init imapClient with host
        self.imap = ImapClient(self.config.host, self.config.port)

        # do trainig
        data = EnronDataset().load_files()
        train_texts, _, train_labels, _ = train_test_split(data.data,
                                                           data.target,
                                                           train_size=0.6)
        train_mails = MailUtils.strings_to_mails(train_texts)
        self.classifier = BayesClassifier(train_mails, train_labels)
        self.classifier.train()

        self.mailChecker = MailChecker(self.imap, self.classifier, self.config)

    def start(self):
        self.imap.login(self.config.username, self.config.password)
        self.mailChecker.start()

    def stop(self):
        self.mailChecker.stop()
        self.imap.logout()
