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

    while True:
        try:
            time.sleep(1)
        except ProgramKilled:
            print("Program killed: running cleanup code")
            sf.stop()
            break
