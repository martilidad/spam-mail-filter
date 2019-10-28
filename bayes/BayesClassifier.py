from sklearn.exceptions import NotFittedError
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from core.NotTrainedException import NotTrainedException
from core.Classifier import Classifier
from core.Mail import Mail
from util import MailUtils


class BayesClassifier(Classifier):

    train_mails: [Mail]
    train_labels: [int]

    def __init__(self, train_mails: [Mail], train_labels: [int]):
        super().__init__(train_mails, train_labels)
        self.train_mails = train_mails
        self.train_labels = train_labels
        self.classifier = MultinomialNB()
        self.vectorizer = CountVectorizer(
            strip_accents='unicode',
            token_pattern=u'(?ui)\\b\\w*[a-z]+\\w*\\b',
            lowercase=True,
            stop_words='english',
            decode_error='replace')

    def train(self):
        vectorized_mails = self.vectorizer.fit_transform(
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
