from configparser import RawConfigParser
from typing import List

from classification.Classifier import Classifier
from classification.DelegatableClassifier import DelegatableClassifier
from classification.DelegatingClassifier import DelegatingClassifier
from classification.bayes.BayesClassifier import BayesClassifier
from classification.blacklist.BlacklistClassifier import BlacklistClassifier
from classification.urlcheck.URLClassifier import URLClassifier
from core.MailAttributes import MailAttributes


class ClassificationConfig:
    """
    ommited config keys will be seen as 0
    sum of weights must be at least 1
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
        },
        "Urls": {
            "Classifier": URLClassifier,
            "Attribute": MailAttributes.BODY,
            "Config-Name": "url_weight",
            "Weight": 0
        },
        "From": {
            "Classifier": BlacklistClassifier,
            "Attribute": MailAttributes.FROM,
            "Config-Name": "from_weight",
            "Weight": 0
        }
    }

    def __init__(self, config_section: RawConfigParser, config):
        self.config = config
        sum = float(0)
        for key in self.INTERNAL_CONFIG.keys():
            subconfig: dict = self.INTERNAL_CONFIG[key]
            weight = config_section.getfloat(subconfig["Config-Name"], '0')
            subconfig["Weight"] = weight
            sum += weight
        if sum < 1:
            raise ValueError(
                "Classification weights must sum up to at least 1. "
                "Use Checkmode None instead, if applicable.")

    def load_classifier(self, train_mails=None,
                        train_labels=None) -> Classifier:
        delegates: List[DelegatableClassifier] = []
        weights: List[float] = []
        for key in self.INTERNAL_CONFIG.keys():
            subconfig: dict = self.INTERNAL_CONFIG[key]
            weight_ = subconfig["Weight"]
            if weight_ == 0:
                continue
            delegate = subconfig["Classifier"](
                train_mails,
                train_labels,
                target_attribute=subconfig["Attribute"],
                config=self.config)
            delegates = [*delegates, delegate]
            weights = [*weights, weight_]
        return DelegatingClassifier(delegates, weights)
