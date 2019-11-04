from core.Mail import Mail
from abc import abstractmethod


class Classifier:
    @abstractmethod
    def __init__(self, train_mails: [Mail] = None, train_labels: [int] = None):
        pass

    @abstractmethod
    def train(self, mails: [Mail] = None, labels: [int] = None):
        pass

    @abstractmethod
    def classify(self, mails: [Mail]) -> [float]:
        pass
