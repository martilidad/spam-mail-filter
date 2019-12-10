from abc import abstractmethod
from typing import List

from classification.Classifier import Classifier
from core.mail.Mail import Mail
from core.mail.MailAttributes import MailAttributes


class DelegatableClassifier(Classifier):
    @abstractmethod
    def __init__(self, train_mails: List[Mail], train_labels: List[int],
                 target_attribute: MailAttributes, config):
        pass
