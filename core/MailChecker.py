from util import MailUtils

import threading


class MailChecker(threading.Thread):
    def __init__(self, interval, imap, classifier):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        self.interval = interval
        self.imap = imap
        self.classifier = classifier

    def run(self):
        self.__mail_check()
        while not self.stopped.wait(self.interval):
            self.__mail_check()

    def __mail_check(self):
        print("checking mails")
        uids = self.imap.get_all_uids()
        for uid in uids:
            # TODO check if uid is new
            payload = self.imap.get_raw_mail_for_uid(uid)
            score = self.classifier.classify(
                MailUtils.strings_to_mails([payload]))
            if score[0] > 0.5:
                print("spam detected")
                # self.imap.move_mail(uid, "[Gmail]/Spam")
            else:
                print("ham detected")

    def stop(self):
        self.stopped.set()
        self.join()
