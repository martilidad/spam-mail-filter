from util import MailUtils, SerializationUtils
import threading


class MailChecker(threading.Thread):
    def __init__(self, imap, classifier, config):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.imap = imap
        self.classifier = classifier
        self.config = config

    def run(self):
        self.__mail_check()
        while not self.stopped.wait(self.config.check_interval * 60):
            self.__mail_check()

    def __retrieve_new_uids(self):
        uids = self.imap.get_all_uids()
        old_checked_uids = SerializationUtils.deserialize(self.config.trackfile)
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
        print("checking mails")
        self.imap.select_mailbox(self.config.inbox)
        new_uids, old_checked_uids = self.__retrieve_new_uids()
        for uid in new_uids:
            payload = self.imap.get_raw_mail_for_uid(uid)
            score = self.classifier.classify(
                MailUtils.strings_to_mails([payload]))
            if score[0] > self.config.score_threshold:
                print("spam detected")
                if not self.config.dryrun and self.config.spam_folder is not None:
                    self.imap.move_mail(uid, self.config.spam_folder)
            else:
                print("ham detected")
        self.__store_new_checke_uids(old_checked_uids, new_uids)

    def stop(self):
        self.stopped.set()
        self.join()
