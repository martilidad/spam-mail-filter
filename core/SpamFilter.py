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
from util import MailUtils, SerializationUtils


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
            train_mails, train_labels = self.__get_usermail_data()
            classifier = self.config.classification_config.load_classifier(
                train_mails, train_labels)
        elif start_mode is StartMode.LIST_MAIL_FOLDERS:
            imap = ImapClient(self.config.host, self.config.port, self.config.ssl)
            imap.login(self.config.username, self.config.password)
            imap.print_valid_folders()
            imap.logout()
            exit(0)
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
        imap = ImapClient(self.config.host, self.config.port, self.config.ssl)
        imap.login(self.config.username, self.config.password)
        batch_size = self.config.batch_size

        imap.select_mailbox(self.config.train_spam_mailbox)
        spam_mb_id = str(
            imap.get_mailbox_identifier(self.config.train_spam_mailbox))
        spam_uids = imap.get_all_uids()[0:self.config.max_train_mails]
        spam_texts = []
        for i in range(0, len(spam_uids), batch_size):
            uids = spam_uids[i:i + batch_size]
            spam_texts += imap.get_mails_for_uids(uids)
        labels = [1] * len(spam_texts)

        imap.select_mailbox(self.config.train_ham_mailbox)
        ham_mb_id = str(
            imap.get_mailbox_identifier(self.config.train_ham_mailbox))
        ham_uids = imap.get_all_uids()[0:self.config.max_train_mails]
        ham_texts = []
        for i in range(0, len(ham_uids), batch_size):
            uids = ham_uids[i:i + batch_size]
            ham_texts += imap.get_mails_for_uids(uids)
        labels = labels + [0] * len(ham_texts)

        if self.config.track_train_mails:
            trained_uids = {
                ham_mb_id: [int(u) for u in ham_uids],
                spam_mb_id: [int(u) for u in spam_uids]
            }
            self.__add_uids_to_trackfile(trained_uids)

        imap.logout()
        return MailUtils.messages_to_mails(spam_texts +
                                           ham_texts), np.array(labels)

    def __add_uids_to_trackfile(self, trained_uids):
        tracked_uids = SerializationUtils.deserialize(self.config.trackfile)
        if tracked_uids is None:
            tracked_uids = {}
        elif type(tracked_uids) is not dict:
            tracked_uids = {}

        keys = set(tracked_uids).union(trained_uids)
        no = []
        merged = dict(
            (k, list(set(tracked_uids.get(k, no) + trained_uids.get(k, no))))
            for k in keys)
        for value in merged.values():
            value.sort()

        SerializationUtils.serialize(merged, self.config.trackfile)
