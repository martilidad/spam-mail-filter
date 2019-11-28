from abc import abstractmethod

from classification.Classifier import Classifier
from core.Mail import Mail
from core.MailAttributes import MailAttributes


class DelegatableClassifier(Classifier):
    @abstractmethod
    def __init__(self, train_mails: [Mail], train_labels: [int],
                 target_attribute: MailAttributes, config):
        pass
