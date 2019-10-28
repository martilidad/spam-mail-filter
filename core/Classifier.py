from core.Mail import Mail
from abc import abstractmethod


class Classifier:
    @abstractmethod
    def __init__(self, train_mails: [Mail], train_labels: [int]):
        pass

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def classify(self, mails: [Mail]) -> [float]:
        pass
