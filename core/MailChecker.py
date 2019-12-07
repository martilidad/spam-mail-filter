import logging
import threading
from typing import List, Tuple, Dict

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

    def __retrieve_new_uids(self, imap, mbid: str) -> Tuple[List[bytes], Dict[str, List[int]]]:
        uids = imap.get_all_uids()
        tracked_uids = SerializationUtils.deserialize(
            self.config.trackfile)
        if tracked_uids is None:
            tracked_uids = {mbid: []}
        elif type(tracked_uids) is not dict:
            tracked_uids = {mbid: []}
        elif mbid not in tracked_uids:
            tracked_uids[mbid] = []
        new_uids = [u for u in uids if int(u) not in tracked_uids[mbid]]
        return new_uids, tracked_uids

    def __store_new_checked_uids(self, mbid: str, tracked_uids: dict,
                                new_uids: List[bytes]):
        new_checked_uids_for_mailbox = list(
            set(tracked_uids[mbid] + [int(u) for u in new_uids]))
        tracked_uids[mbid] = new_checked_uids_for_mailbox
        SerializationUtils.serialize(tracked_uids, self.config.trackfile)

    def __mail_check(self):
        logging.info("checking mails")
        imap = ImapClient(self.config.host, self.config.port)
        imap.login(self.config.username, self.config.password)
        imap.select_mailbox(self.config.inbox)
        mbid = str(imap.get_mailbox_identifier(self.config.inbox))
        new_uids, tracked_uids = self.__retrieve_new_uids(imap, mbid)
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
        self.__store_new_checked_uids(mbid, tracked_uids, new_uids)
        imap.logout()
        logging.debug("mailcheck complete")

    def stop(self):
        self.stopped.set()
        self.join()
