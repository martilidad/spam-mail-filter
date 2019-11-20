from configparser import SectionProxy

from classification.Classifier import Classifier
from classification.DelegatableClassifiers import DelegatableClassifiers
from core.Mail import Mail
from core.MailAttributes import MailAttributes
from core.Serializable import T


class DelegatingClassifier(Classifier):

    def serialize(self):
        for delegate in self.delegates:
            delegate.serialize()

    def deserialize(self) -> T:
        # TODO
        pass

    def __init__(self, train_mails: [Mail] = None, train_labels: [int] = None, config=None):
        super().__init__(train_mails, train_labels)
        if config is None:
            raise ValueError("Delegating classifier needs a valid config.")
        attributes, classifiers, self.weights = self.parse_config(config)
        self.delegates: [Classifier] = []
        for attribute, classifier in zip(attributes, classifiers):
            self.delegates = [*self.delegates, classifier(target_attribute=attribute)]

    def train(self, mails: [Mail] = None, labels: [int] = None):
        for delegate in self.delegates:
            delegate.train(mails, labels)

    def classify(self, mails: [Mail]) -> [float]:
        scores = [0 for val in range(len(mails))]
        for delegate, weight in zip(self.delegates, self.weights):
            # could this happen more efficient?
            scores = [score * weight + prev_score for score, prev_score in zip(delegate.classify(mails), scores)]


    @staticmethod
    def parse_config(configSection: SectionProxy) -> ([MailAttributes], [Classifier], [float]):
        attributes = []
        classifiers = []
        weights = []
        for attribute in configSection:
            attributes = [*attributes, attribute]
            split = configSection.get(attribute).split(':')
            if len(split) != 2:
                raise ValueError("Error on config key: " + attribute + " Every "
                                                   "key in section classifiers needs a valid classifier and weight.")
            classifiers = [*classifiers, DelegatableClassifiers[split[0]].value]
            weights = [*weights, float(split[1])]
        if sum(weights) != 1:
            raise ValueError("Classifier weights should sum up to 1. Please check the classifiers config section.")
        return attributes, classifiers, weights


