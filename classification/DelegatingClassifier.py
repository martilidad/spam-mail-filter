from classification.Classifier import Classifier
from core.Mail import Mail
from core.Serializable import T


class DelegatingClassifier(Classifier):
    def __init__(self, delegates, weights):
        self.weights: [float] = weights
        self.delegates: [Classifier] = delegates

    def train(self, mails: [Mail] = None, labels: [int] = None):
        for delegate in self.delegates:
            delegate.train(mails, labels)

    def classify(self, mails: [Mail]) -> [float]:
        scores = [0 for val in range(len(mails))]
        for delegate, weight in zip(self.delegates, self.weights):
            # could this happen more efficient?
            scores = [
                score * weight + prev_score
                for score, prev_score in zip(delegate.classify(mails), scores)
            ]
        return scores

    @property
    def save_folder(self):
        return "classifier/"

    def serialize(self, sub_folder: str = None):
        base_folder = self.resolve_folder(sub_folder)
        for delegate in self.delegates:
            delegate.serialize(base_folder)

    def deserialize(self, sub_folder: str = None) -> T:
        base_folder = self.resolve_folder(sub_folder)
        new_delegates = []
        for delegate in self.delegates:
            new_delegates = [*new_delegates, delegate.deserialize(base_folder)]
