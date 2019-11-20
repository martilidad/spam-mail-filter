from enum import Enum

from classification.bayes.BayesClassifier import BayesClassifier


# TODO add Classvar Classifier as type
class DelegatableClassifiers(Enum):
    BAYES = BayesClassifier
