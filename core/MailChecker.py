from serialization.Serializer import Serializer
from util import MailUtils

import threading


class MailChecker(threading.Thread):
    def __init__(self, interval, imap, classifier):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.interval = interval
        self.imap = imap
        self.classifier = classifier
        self.serializer = Serializer()

    def run(self):
        self.__mail_check()
        while not self.stopped.wait(self.interval):
            self.__mail_check()

    def __retrieve_new_uids(self):
        uids = self.imap.get_all_uids()
        old_checked_uids = self.serializer.deserialize("trackfile.trc")
        if old_checked_uids is None:
            old_checked_uids = []
        new_uids = [u for u in uids if int(u) not in old_checked_uids]
        return new_uids, old_checked_uids

    def __store_new_checke_uids(self, old_checked_uids: [int], new_uids: [bytes]):
        new_checked_uids = list(set(old_checked_uids + [int(u) for u in new_uids]))
        self.serializer.serialize(new_checked_uids, "trackfile.trc")

    def __mail_check(self):
        print("checking mails")
        new_uids, old_checked_uids = self.__retrieve_new_uids()
        for uid in new_uids:
            payload = self.imap.get_raw_mail_for_uid(uid)
            score = self.classifier.classify(
                MailUtils.strings_to_mails([payload]))
            if score[0] > 0.5:
                print("spam detected")
                # self.imap.move_mail(uid, "[Gmail]/Spam")
            else:
                print("ham detected")
        self.__store_new_checke_uids(old_checked_uids, new_uids)

    def stop(self):
        self.stopped.set()
        self.join()
