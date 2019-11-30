import logging

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
        logging.debug("Completed Loading the Classifier")

        if self.config.check_mode is CheckMode.NONE:
            logging.info("Shutting down because check_mode is none")
            self.classifier.serialize()
            exit(0)

        self.mailChecker = MailChecker(self.classifier, self.config)

    def __load_initial_classifier(self) -> Classifier:
        start_mode = self.config.start_mode
        if start_mode is StartMode.TRAINING:
            logging.debug("Starting to load training data from disk.")
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
            logging.debug("Starting to load training data from mail server.")
            if self.config.train_ham_mailbox is None or self.config.train_spam_mailbox is None:
                raise ValueError(
                    "Need configured training mailboxes for USERMAIL_TRAINING")
            train_mails, train_labels = self.__get_usermail_data()
            classifier = self.config.classification_config.load_classifier(
                train_mails, train_labels)
        else:
            raise ValueError("Invalid value for start mode")
        logging.debug("Starting training.")
        classifier.train()
        return classifier

    def start(self):
        self.mailChecker.start()

    def stop(self):
        self.mailChecker.stop()
        self.classifier.serialize()

    def __get_usermail_data(self):
        # TODO trained mails should be added to trackfile
        imap = ImapClient(self.config.host, self.config.port)
        imap.login(self.config.username, self.config.password)
        batch_size = self.config.batch_size
        max_train_mails = self.config.max_train_mails

        imap.select_mailbox(self.config.train_spam_mailbox)
        spam_uids = imap.get_all_uids()
        spam_texts = []
        for i in range(0, max_train_mails, batch_size):
            end = min(i + batch_size, max_train_mails)
            uids = spam_uids[i:end]
            if not uids:
                break
            spam_texts += imap.get_mails_for_uids(uids)
        labels = [1] * len(spam_texts)

        imap.select_mailbox(self.config.train_ham_mailbox)
        ham_uids = imap.get_all_uids()
        ham_texts = []
        for i in range(0, max_train_mails, batch_size):
            end = min(i + batch_size, max_train_mails)
            uids = ham_uids[i:end]
            if not uids:
                break
            ham_texts += imap.get_mails_for_uids(uids)
        labels = labels + [0] * len(ham_texts)

        imap.logout()
        return MailUtils.messages_to_mails(spam_texts +
                                           ham_texts), np.array(labels)
