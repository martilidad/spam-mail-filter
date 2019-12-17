import logging
import signal
import time

from core.SpamFilter import SpamFilter


class ProgramKilled(Exception):
    pass


def signal_handler(signum, frame):
    raise ProgramKilled


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    sf = SpamFilter()
    sf.start()

    while sf.is_alive():
        try:
            time.sleep(1)
        except ProgramKilled:
            logging.debug("Program killed: running cleanup code")
            sf.stop()
            break
    logging.debug("One or more Threads unexpectedly terminated: running cleanup code")
    sf.stop()
