from configparser import RawConfigParser

from classification.Classifier import Classifier
from classification.DelegatingClassifier import DelegatingClassifier
from classification.bayes.BayesClassifier import BayesClassifier
from core.MailAttributes import MailAttributes


class ClassificationConfig:
    """
    ommited config keys will be seen as 0
    sum of weights must be 1
    """

    INTERNAL_CONFIG: dict = {
        "Body": {
            "Classifier": BayesClassifier,
            "Attribute": MailAttributes.BODY,
            "Config-Name": "body_weight",
            "Weight": 0
        },
        "Subject": {
            "Classifier": BayesClassifier,
            "Attribute": MailAttributes.SUBJECT,
            "Config-Name": "subject_weight",
            "Weight": 0
        }
    }

    def __init__(self, config_section: RawConfigParser):
        sum = 0
        for key in self.INTERNAL_CONFIG.keys():
            subconfig: dict = self.INTERNAL_CONFIG[key]
            weight = config_section.getfloat(subconfig["Config-Name"], 0)
            subconfig["Weight"] = weight
            sum += weight
        if sum != 1:
            raise ValueError("Classification weights must sum up to 1")

    def load_classifier(self, train_mails=None,
                        train_labels=None) -> Classifier:
        delegates = []
        weights = []
        for key in self.INTERNAL_CONFIG.keys():
            subconfig: dict = self.INTERNAL_CONFIG[key]
            delegate = subconfig["Classifier"](
                train_mails,
                train_labels,
                target_attribute=subconfig["Attribute"])
            delegates = [*delegates, delegate]
            weights = [*weights, subconfig["Weight"]]
        return DelegatingClassifier(delegates, weights)
