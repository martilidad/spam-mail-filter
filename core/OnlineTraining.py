import logging
import threading


class OnlineTraining(threading.Thread):

    def __init__(self, lock, spamFilter):
        super().__init__()
        self.lock = lock
        self.spamFilter = spamFilter
        self.running = True

    def run(self):
        while self.running:
            inp = input()
            if inp == "train":
                self.lock.acquire()
                logging.info("starting training")
                self.spamFilter.train_online()
                logging.info("finished training")
                self.lock.release()

    def stop(self):
        self.running = False
        self.join()
