from scipy import sparse
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.exceptions import NotFittedError
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from core.Classifier import Classifier
from core.Mail import Mail
from core.NotTrainedException import NotTrainedException
from core.Serializable import Serializable, T
from util import MailUtils, SerializationUtils


class BayesClassifier(Classifier, Serializable['BayesClassifier']):

    save_folder = "bayes_classifier/"

    def __init__(self, train_mails: [Mail] = None, train_labels: [int] = None):
        super().__init__(train_mails, train_labels)
        self.vocabulary: dict = {}
        self.vectorizer: CountVectorizer
        self.vectorized_mails: csr_matrix
        if train_mails is not None and train_labels is not None:
            self.train_labels = train_labels
            self.update_vocabulary(train_mails)
            self.vectorized_mails: csr_matrix = self.vectorizer.transform(
                MailUtils.mails_to_strings(train_mails))
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
        vocab, _ = vectorizer._count_vocab(MailUtils.mails_to_strings(mails),
                                           False)
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
                MailUtils.mails_to_strings(mails))
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
            MailUtils.mails_to_strings(mails))
        try:
            return self.classifier.predict(vectorized_mails)
        except NotFittedError:
            raise NotTrainedException(
                "This BayesClassifier instance is not trained yet. "
                "Call train() before using this method.")

    def serialize(self):
        base_folder = SerializationUtils.get_absolute_file_path(self.save_folder)
        np.save(base_folder + "/labels", self.train_labels)
        sparse.save_npz(base_folder + "/mails", self.vectorized_mails)
        SerializationUtils.serialize(self.vocabulary, self.save_folder + "vocab")

    @staticmethod
    def deserialize() -> 'BayesClassifier':
        instance = BayesClassifier()
        base_folder = SerializationUtils.get_absolute_file_path(instance.save_folder)
        instance.train_labels = np.load(base_folder + "/labels" + ".npy")
        instance.vectorized_mails = sparse.load_npz(base_folder + "/mails" + ".npz")
        instance.vocabulary = SerializationUtils.deserialize(instance.save_folder + "vocab")
        instance.vectorizer = instance.create_vectorizer(instance.vocabulary)
        return instance
