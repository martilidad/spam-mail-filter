import numpy as np
from sklearn.model_selection import train_test_split

from classification.Classifier import Classifier
from core.CheckMode import CheckMode
from core.Config import Config
from core.EnronDataset import EnronDataset
from core.MailChecker import MailChecker
from core.StartMode import StartMode
from imap.ImapClient import ImapClient
from util import MailUtils


class SpamFilter:
    def __init__(self):
        self.config = Config()

        self.classifier = self.__load_initial_classifier()
        print("Completed Loading the Classifier")

        if self.config.check_mode is CheckMode.NONE:
            print("Shutting down because check_mode is none")
            self.classifier.serialize()
            exit(0)

        self.mailChecker = MailChecker(self.classifier, self.config)

    def __load_initial_classifier(self) -> Classifier:
        start_mode = self.config.start_mode
        if start_mode is StartMode.TRAINING:
            # do trainig
            data = EnronDataset().load_files()
            train_texts, _, train_labels, _ = train_test_split(data.data,
                                                               data.target,
                                                               train_size=0.6)
            train_mails = [
                EnronDataset.enron_string_to_mail(text) for text in train_texts
            ]
            classifier = self.config.classification_config.load_classifier(
                train_mails, train_labels)
        elif start_mode is StartMode.PRETRAINED:
            classifier = self.config.classification_config.load_classifier()
            classifier.deserialize()
        elif start_mode is StartMode.NO_TRAINING:
            return self.config.classification_config.load_classifier()
        elif start_mode is StartMode.USERMAIL_TRAINING:
            if self.config.train_ham_mailbox is None or self.config.train_spam_mailbox is None:
                raise ValueError(
                    "Need configured training mailboxes for USERMAIL_TRAINING")
            train_mails, train_labels = self.__get_usermail_data()
            classifier = self.config.classification_config.load_classifier(
                train_mails, train_labels)
        else:
            raise ValueError("Invalid value for start mode")

        classifier.train()
        return classifier

    def start(self):
        self.mailChecker.start()

    def stop(self):
        self.mailChecker.stop()
        self.classifier.serialize()

    def __get_usermail_data(self):
        # TODO trained mails should be added to trackfile
        # what if spam or ham folder is much bigger than the other one?
        imap = ImapClient(self.config.host, self.config.port)
        imap.login(self.config.username, self.config.password)
        texts = []
        labels = []

        imap.select_mailbox(self.config.train_spam_mailbox)
        spam_uids = imap.get_all_uids()
        for i, uid in enumerate(spam_uids):
            if i >= self.config.max_train_mails:
                break
            message = imap.get_mail_for_uid(uid)
            texts.append(message)
            labels.append(1)  # label 1 is "spam"

        imap.select_mailbox(self.config.train_ham_mailbox)
        ham_uids = imap.get_all_uids()
        for i, uid in enumerate(ham_uids):
            if i >= self.config.max_train_mails:
                break
            message = imap.get_mail_for_uid(uid)
            texts.append(message)
            labels.append(0)  # label 0 is "ham"

        imap.logout()
        return MailUtils.messages_to_mails(texts), np.array(labels)
