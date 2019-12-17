import logging
from email.message import Message
from threading import Lock
from typing import List

import numpy as np
from sklearn.model_selection import train_test_split

from classification.Classifier import Classifier
from core.OnlineTraining import OnlineTraining
from core.config.CheckMode import CheckMode
from core.config.Config import Config
from core.config.StartMode import StartMode
from core.data.EnronDataset import EnronDataset
from core.mail.MailChecker import MailChecker
from imap.ImapClient import ImapClient
from util import MailUtils, SerializationUtils


class SpamFilter:
    def __init__(self):
        self.train_trackfile = "train_trackfile.trc"
        self.config = Config()

        self.classifier = self.__load_initial_classifier()
        logging.debug("Completed Loading the Classifier")

        if self.config.check_mode is CheckMode.NONE:
            logging.info("Shutting down because check_mode is none")
            exit(0)

        lock = Lock()
        self.mailChecker = MailChecker(self.classifier, self.config, lock)
        self.onlineTraining = OnlineTraining(lock, self)

    def __load_initial_classifier(self) -> Classifier:
        start_mode = self.config.start_mode
        classifier: Classifier
        deserialize = True
        train_mails = None
        train_labels = None
        if start_mode is StartMode.TESTDATA_TRAINING:
            logging.debug("Starting to load training data from disk.")
            # do trainig
            data = EnronDataset().load_files()
            train_texts, _, train_labels, _ = train_test_split(data.data,
                                                               data.target,
                                                               train_size=0.6)
            train_mails = [
                EnronDataset.enron_string_to_mail(text) for text in train_texts
            ]
            deserialize = False
        elif start_mode is StartMode.PRETRAINED:
            pass
        elif start_mode is StartMode.NO_TRAINING:
            deserialize = False
        elif start_mode is StartMode.USERMAIL_TRAINING:
            logging.debug("Starting to load training data from mail server.")
            SerializationUtils.clear_trackfile(self.train_trackfile)
            train_mails, train_labels = self.__get_usermail_data()
            deserialize = False
        elif start_mode is StartMode.ONLINE_TRAINING:
            logging.debug("Starting to load training data from mail server.")
            train_mails, train_labels = self.__get_usermail_data()
        elif start_mode is StartMode.LIST_MAIL_FOLDERS:
            imap = ImapClient(self.config.host, self.config.port,
                              self.config.ssl)
            imap.login(self.config.username, self.config.password)
            imap.print_valid_folders()
            imap.logout()
            return exit(0)
        else:
            raise ValueError("Invalid value for start mode")
        classifier = self.config.classification_config.load_classifier()
        if deserialize:
            classifier.deserialize()
        classifier.train(train_mails, train_labels)
        classifier.serialize()
        return classifier

    def start(self):
        self.mailChecker.start()
        if self.__is_online_training_active():
            self.onlineTraining.start()

    def __is_online_training_active(self):
        return self.config.start_mode is StartMode.USERMAIL_TRAINING \
               or self.config.start_mode is StartMode.ONLINE_TRAINING

    def stop(self):
        self.mailChecker.stop()
        self.classifier.serialize()
        self.onlineTraining.stop()

    def train_online(self):
        train_mails, train_labels = self.__get_usermail_data()
        self.classifier.train(train_mails, train_labels)
        self.classifier.serialize()

    def __get_usermail_data(self):
        try:
            imap = ImapClient(self.config.host, self.config.port, self.config.ssl)
            imap.login(self.config.username, self.config.password)

            spam_texts, spam_uids, spam_mb_id = self.__get_train_mails_for_mailbox(imap, self.config.train_spam_mailbox)
            labels = [1] * len(spam_texts)

            ham_texts, ham_uids, ham_mb_id = self.__get_train_mails_for_mailbox(imap, self.config.train_ham_mailbox)
            labels = labels + [0] * len(ham_texts)

            trained_uids = {
                ham_mb_id: [int(u) for u in ham_uids],
                spam_mb_id: [int(u) for u in spam_uids]
            }
            SerializationUtils.add_uids_to_trackfile(self.train_trackfile, trained_uids)

            imap.logout()
            return MailUtils.messages_to_mails(spam_texts +
                                               ham_texts), np.array(labels)
        except TimeoutError as e:
            logging.fatal('Timeout occurred while retrieving mails for training; maybe you lost connection')
            raise e

    def __get_train_mails_for_mailbox(self, imap, mailbox: str):
        imap.select_mailbox(mailbox)
        uids, mbid = imap.get_new_uids(mailbox, self.train_trackfile)
        uids = uids[0:self.config.max_train_mails]
        texts: List[Message] = []
        for i in range(0, len(uids), self.config.batch_size):
            batch_uids = uids[i:i + self.config.batch_size]
            texts += imap.get_mails_for_uids(batch_uids)
        return texts, uids, mbid

    def is_alive(self):
        alive = self.mailChecker.is_alive()
        if self.__is_online_training_active():
            alive &= self.onlineTraining.is_alive()
        return alive
