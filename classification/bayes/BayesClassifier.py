import json
import os

import numpy as np
from scipy import sparse
from scipy.sparse import csr_matrix
from sklearn.exceptions import NotFittedError
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from classification.DelegatableClassifier import DelegatableClassifier
from core.Mail import Mail
from core.MailAttributes import MailAttributes
from core.NotTrainedException import NotTrainedException
from core.Serializable import Serializable


class BayesClassifier(DelegatableClassifier, Serializable['BayesClassifier']):
    save_folder = "bayes_classifier/"

    def __init__(self,
                 train_mails: [Mail] = None,
                 train_labels: [int] = None,
                 target_attribute=MailAttributes.BODY):
        super().__init__(train_mails, train_labels, target_attribute)
        self.vocabulary: dict = {}
        self.vectorizer: CountVectorizer
        self.vectorized_mails: csr_matrix
        self.target_attribute: MailAttributes = target_attribute
        if train_mails is not None and train_labels is not None:
            self.train_labels = train_labels
            self.update_vocabulary(train_mails)
            self.vectorized_mails: csr_matrix = self.vectorizer. \
                transform([self.target_attribute(mail) for mail in train_mails])
        else:
            self.vectorized_mails = None
            self.train_labels: [int] = []
        self.classifier = MultinomialNB()

    @staticmethod
    def create_vectorizer(vocabulary=None) -> CountVectorizer:
        return CountVectorizer(strip_accents='unicode',
                               token_pattern=u'(?ui)\\b\\w*[a-z]+\\w*\\b',
                               lowercase=True,
                               stop_words='english',
                               decode_error='replace',
                               vocabulary=vocabulary)

    def update_vocabulary(self, mails: [Mail]):
        # TODO move this messy code to a custom vectorizer and limit vocabulary
        # see CountVectorizer.fit_transform for limit example
        # vectorizer without vocabulary
        vectorizer = self.create_vectorizer()
        vocab, _ = vectorizer._count_vocab(
            [self.target_attribute(mail) for mail in mails], False)
        # merge vocabularies
        i = len(self.vocabulary)
        for key in vocab.keys():
            if key not in self.vocabulary.keys():
                self.vocabulary[key] = i
                i += 1
        # update vectorizer
        self.vectorizer = self.create_vectorizer(self.vocabulary)

    def train(self, mails: [Mail] = None, labels: [int] = None):
        if mails is not None and labels is not None:
            self.train_labels = [*self.train_labels, *labels]
            self.update_vocabulary(mails)
            # most resilient list concatenation
            vector: csr_matrix = self.vectorizer.transform(
                [self.target_attribute(mail) for mail in mails])
            if self.vectorized_mails is not None:
                vector.resize(vector.shape[0], len(self.vocabulary))
                self.vectorized_mails.resize(self.vectorized_mails.shape[0],
                                             len(self.vocabulary))
                self.vectorized_mails = sparse.vstack(
                    (self.vectorized_mails, vector))
            else:
                self.vectorized_mails = vector
        elif self.vectorized_mails is None:
            raise RuntimeError("the Classifier needs data")
        self.classifier.fit(self.vectorized_mails, self.train_labels)

    def classify(self, mails: [Mail]) -> [float]:
        vectorized_mails = self.vectorizer.transform(
            [self.target_attribute(mail) for mail in mails])
        try:
            return self.classifier.predict(vectorized_mails)
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
            json.dump(self.vocabulary, wfile)

    def deserialize(self, sub_folder: str = None) -> 'BayesClassifier':
        base_folder = self.resolve_folder(
            sub_folder) + self.target_attribute.__name__ + "/"
        self.train_labels = np.load(base_folder + "/labels" + ".npy")
        self.vectorized_mails = sparse.load_npz(base_folder + "/mails" +
                                                ".npz")
        with open(base_folder + "/vocab", 'r') as rfile:
            self.vocabulary = json.load(rfile)
        self.vectorizer = self.create_vectorizer(self.vocabulary)
        return self
