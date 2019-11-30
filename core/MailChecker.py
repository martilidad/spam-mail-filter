import logging
import threading

from core.CheckMode import CheckMode
from imap.ImapClient import ImapClient
from util import MailUtils, SerializationUtils


class MailChecker(threading.Thread):
    def __init__(self, classifier, config):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.classifier = classifier
        self.config = config

    def run(self):
        self.__mail_check()
        while not self.stopped.wait(self.config.check_interval * 60):
            self.__mail_check()

    def __retrieve_new_uids(self, imap):
        uids = imap.get_all_uids()
        old_checked_uids = SerializationUtils.deserialize(
            self.config.trackfile)
        if old_checked_uids is None:
            old_checked_uids = []
        new_uids = [u for u in uids if int(u) not in old_checked_uids]
        return new_uids, old_checked_uids

    def __store_new_checke_uids(self, old_checked_uids: [int],
                                new_uids: [bytes]):
        new_checked_uids = list(
            set(old_checked_uids + [int(u) for u in new_uids]))
        SerializationUtils.serialize(new_checked_uids, self.config.trackfile)

    def __mail_check(self):
        logging.info("checking mails")
        imap = ImapClient(self.config.host, self.config.port)
        imap.login(self.config.username, self.config.password)
        imap.select_mailbox(self.config.inbox)
        new_uids, old_checked_uids = self.__retrieve_new_uids(imap)
        for i in range(0, len(new_uids), self.config.batch_size):
            uids = new_uids[i:i + self.config.batch_size]
            messages = imap.get_mails_for_uids(uids)
            scores = self.classifier.classify(
                MailUtils.messages_to_mails(messages))
            for score, uid in zip(scores, uids):
                if score > self.config.score_threshold:
                    logging.debug("spam detected")
                    if self.config.check_mode is CheckMode.NORMAL and self.config.spam_folder is not None:
                        imap.move_mail(uid, self.config.spam_folder)
                    elif self.config.check_mode is CheckMode.FLAGGING:
                        imap.flag_mail(uid)
                    # else DRYRUN: nothing to do
                else:
                    logging.debug("ham detected")
        self.__store_new_checke_uids(old_checked_uids, new_uids)
        imap.logout()
        logging.debug("mailcheck complete")

    def stop(self):
        self.stopped.set()
        self.join()
