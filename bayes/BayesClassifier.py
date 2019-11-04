from scipy import sparse
from scipy.sparse import csr_matrix
from sklearn.exceptions import NotFittedError
from sklearn.feature_extraction.text import HashingVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from core.Classifier import Classifier
from core.Mail import Mail
from core.NotTrainedException import NotTrainedException
from util import MailUtils


class BayesClassifier(Classifier):
    def __init__(self, train_mails: [Mail] = None, train_labels: [int] = None):
        super().__init__(train_mails, train_labels)
        if train_mails is not None and train_labels is not None:
            self.train_mails = train_mails
            self.train_labels = train_labels
            self.update_vocabulary(train_mails)
        else:
            self.train_mails: [Mail] = []
            self.train_labels: [int] = []
            self.vocabulary: dict = {}
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
            self.update_vocabulary(mails)
            # most resilient list concatenation
            self.train_mails = [*self.train_mails, *mails]
            self.train_labels = [*self.train_labels, *labels]
        vectorized_mails = self.vectorizer.transform(
            MailUtils.mails_to_strings(self.train_mails))
        self.classifier.fit(vectorized_mails, self.train_labels)

    def classify(self, mails: [Mail]) -> [float]:
        vectorized_mails = self.vectorizer.transform(
            MailUtils.mails_to_strings(mails))
        try:
            return self.classifier.predict(vectorized_mails)
        except NotFittedError:
            raise NotTrainedException(
                "This BayesClassifier instance is not trained yet. "
                "Call train() before using this method.")
