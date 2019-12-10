from abc import abstractmethod
from typing import List

from core.mail.Mail import Mail
from util.Serializable import Serializable


class Classifier(Serializable):
    @abstractmethod
    def train(self, mails: List[Mail] = None, labels: List[int] = None):
        pass

    @abstractmethod
    def classify(self, mails: List[Mail]) -> List[float]:
        pass
