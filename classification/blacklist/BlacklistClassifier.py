from typing import List

from classification.DelegatableClassifier import DelegatableClassifier
from core.Mail import Mail
from core.MailAttributes import MailAttributes
from util import SerializationUtils


class BlacklistClassifier(DelegatableClassifier):
    def __init__(self, train_mails: List[Mail], train_labels: List[int], target_attribute: MailAttributes, config):
        super().__init__(train_mails, train_labels, target_attribute, config)
        self.target_attribute = target_attribute
        self.blacklist_file = "blacklist/" + self.target_attribute.__name__

    def train(self, mails: List[Mail] = None, labels: List[int] = None):
        pass

    def classify(self, mails: List[Mail]) -> List[float]:
        blacklist = self.__load_blacklist()
        scores = []
        for mail in mails:
            text = self.target_attribute(mail)
            scores.append(float(any(sender in text for sender in blacklist)))

        return scores

    def __load_blacklist(self):
        blacklist = SerializationUtils.deserialize(self.blacklist_file)
        return blacklist if blacklist is not None else []

    @property
    def save_folder(self):
        return None

    def serialize(self, sub_folder: str = None):
        pass

    def deserialize(self, sub_folder: str = None) -> 'BlacklistClassifier':
        return self
