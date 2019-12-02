import json
import os
from typing import List

import numpy as np
from scipy import sparse
from scipy.sparse import csr_matrix
from sklearn.exceptions import NotFittedError
from sklearn.naive_bayes import MultinomialNB

from classification.DelegatableClassifier import DelegatableClassifier
from classification.bayes.OnlineCountVectorizer import OnlineCountVectorizer
from core.Mail import Mail
from core.MailAttributes import MailAttributes
from core.NotTrainedException import NotTrainedException
from core.Serializable import Serializable


class BayesClassifier(DelegatableClassifier, Serializable['BayesClassifier']):
    save_folder = "bayes_classifier/"

    def __init__(self,
                 train_mails: List[Mail] = None,
                 train_labels: List[int] = None,
                 target_attribute=MailAttributes.BODY,
                 config=None):
        super().__init__(train_mails, train_labels, target_attribute, config)
        self.vectorizer: OnlineCountVectorizer = OnlineCountVectorizer()
        self.vectorized_mails: csr_matrix
        self.target_attribute: MailAttributes = target_attribute
        if train_mails is not None and train_labels is not None:
            self.train_labels = train_labels
            self.vectorized_mails = self.vectorizer. \
                fit_transform([self.target_attribute(mail) for mail in train_mails])
        else:
            self.vectorized_mails = None
            self.train_labels = []
        self.classifier = MultinomialNB()

    def train(self, mails: List[Mail] = None, labels: List[int] = None):
        if mails is not None and labels is not None:
            self.train_labels = [*self.train_labels, *labels]
            # most resilient list concatenation
            vector: csr_matrix = self.vectorizer.fit_transform(
                [self.target_attribute(mail) for mail in mails])
            if self.vectorized_mails is not None:
                self.vectorized_mails = self.vectorizer.combine(
                    self.vectorized_mails, vector)
            else:
                self.vectorized_mails = vector
        elif self.vectorized_mails is None:
            raise RuntimeError("the Classifier needs data")
        self.classifier.fit(self.vectorized_mails, self.train_labels)

    def classify(self, mails: List[Mail]) -> List[float]:
        vectorized_mails = self.vectorizer.transform(
            [self.target_attribute(mail) for mail in mails])
        try:
            return self.classifier.predict_proba(vectorized_mails)[:, 1]
        except NotFittedError:
            raise NotTrainedException(
                "This BayesClassifier instance is not trained yet. "
                "Call train() before using this method.")

    def serialize(self, sub_folder: str = None):
        # TODO clean up messy serialization code
        base_folder = self.resolve_folder(
            sub_folder) + self.target_attribute.__name__ + "/"
        os.makedirs(base_folder, exist_ok=True)
        np.save(base_folder + "/labels", self.train_labels)
        sparse.save_npz(base_folder + "/mails", self.vectorized_mails)
        with open(base_folder + "/vocab", 'w+') as wfile:
            json.dump(self.vectorizer.vocabulary, wfile, default=self.convert)

    @staticmethod
    def convert(o):
        if isinstance(o, np.integer):
            return int(o)
        raise TypeError("Unable to serialize " + o.dtype)

    def deserialize(self, sub_folder: str = None) -> 'BayesClassifier':
        base_folder = self.resolve_folder(
            sub_folder) + self.target_attribute.__name__ + "/"
        self.train_labels = np.load(base_folder + "/labels" + ".npy")
        self.vectorized_mails = sparse.load_npz(base_folder + "/mails" +
                                                ".npz")
        with open(base_folder + "/vocab", 'r') as rfile:
            vocabulary = json.load(rfile)
            self.vectorizer = OnlineCountVectorizer(vocabulary)
        return self
