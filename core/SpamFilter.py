from sklearn.model_selection import train_test_split

from bayes.BayesClassifier import BayesClassifier
from core.CheckMode import CheckMode
from core.Config import Config
from core.EnronDataset import EnronDataset
from core.UsermailDataset import UsermailDataset
from core.MailChecker import MailChecker
from core.StartMode import StartMode
from imap.ImapClient import ImapClient
from util import MailUtils, SerializationUtils
import shutil


class SpamFilter:
    def __init__(self):
        self.config = Config()

        self.classifier = self.load_initial_classifier()
        print("Completed Loading the Classifier")

        if self.config.check_mode is CheckMode.NONE:
            print("Shutting down because check_mode is none")
            self.classifier.serialize()
            exit(0)

        # init imapClient with host
        self.imap = ImapClient(self.config.host, self.config.port)
        self.mailChecker = MailChecker(self.imap, self.classifier, self.config)

    def load_initial_classifier(self) -> BayesClassifier:
        start_mode = self.config.start_mode
        if start_mode is StartMode.TRAINING:
            # do trainig
            data = EnronDataset().load_files()
            train_texts, _, train_labels, _ = train_test_split(data.data,
                                                               data.target,
                                                               train_size=0.6)
            train_mails = MailUtils.strings_to_mails(train_texts)
            classifier = BayesClassifier(train_mails, train_labels)
        elif start_mode is StartMode.PRETRAINED:
            classifier = BayesClassifier.deserialize()
        elif start_mode is StartMode.NO_TRAINING:
            return BayesClassifier()
        elif start_mode is StartMode.USERMAIL_TRAINING:
            if self.config.train_ham_mailbox is None or self.config.train_spam_mailbox is None:
                raise ValueError(
                    "Need configured training mailboxes for USERMAIL_TRAINING")
            data = self.get_usermail_data()
            train_texts, _, train_labels, _ = train_test_split(data.data,
                                                               data.target,
                                                               train_size=0.6)
            train_mails = MailUtils.strings_to_mails(train_texts)
            classifier = BayesClassifier(train_mails, train_labels)
        classifier.train()
        return classifier

    def start(self):
        self.imap.login(self.config.username, self.config.password)
        self.mailChecker.start()

    def stop(self):
        self.mailChecker.stop()
        self.imap.logout()
        self.classifier.serialize()

    def get_usermail_data(self):
        # TODO trained mails should be added to trackfile
        # what if spam or ham folder is much bigger than the other one?
        imap = ImapClient(self.config.host, self.config.port)
        imap.login(self.config.username, self.config.password)

        imap.select_mailbox(self.config.train_spam_mailbox)
        spam_uids = imap.get_all_uids()
        for i, uid in enumerate(spam_uids):
            message = imap.get_mail_for_uid(uid)
            mail = MailUtils.messages_to_strings([message])

            filename = "/USERMAIL/spam/spam" + str(i) + ".txt"
            SerializationUtils.serialize(mail, filename)

        imap.select_mailbox(self.config.train_ham_mailbox)
        ham_uids = imap.get_all_uids()
        for i, uid in enumerate(ham_uids):
            message = imap.get_mail_for_uid(uid)
            mail = MailUtils.messages_to_strings([message])

            filename = "USERMAIL/ham/ham" + str(i) + ".txt"
            SerializationUtils.serialize(mail, filename)

        imap.logout()

        data = UsermailDataset().load_files()

        usermail_dir = SerializationUtils.get_absolute_file_path("/USERMAIL")
        shutil.rmtree(usermail_dir, ignore_errors=True)
        return data
