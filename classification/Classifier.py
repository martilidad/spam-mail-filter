from abc import abstractmethod

from core.Mail import Mail
from core.Serializable import Serializable


class Classifier(Serializable):
    @abstractmethod
    def train(self, mails: [Mail] = None, labels: [int] = None):
        pass

    @abstractmethod
    def classify(self, mails: [Mail]) -> [float]:
        pass
