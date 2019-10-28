from unittest import TestCase

from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from bayes.BayesClassifier import BayesClassifier
from core.EnronDataset import EnronDataset
from util import MailUtils


class TestBayesClassifier(TestCase):
    def test_classify(self):
        data = EnronDataset().load_files()
        train_texts, test_texts, train_labels, test_labels = train_test_split(
            data.data, data.target, train_size=0.6)
        train_mails = MailUtils.strings_to_mails(train_texts)
        test_mails = MailUtils.strings_to_mails(test_texts)
        classifier = BayesClassifier(train_mails, train_labels)
        classifier.train()
        predictions = classifier.classify(test_mails)

        accuracy = accuracy_score(test_labels, predictions)
        self.assertGreater(accuracy, 0.9)
        print('Accuracy score: ', accuracy)
        print('Precision score: ', precision_score(test_labels, predictions))
        print('Recall score: ', recall_score(test_labels, predictions))
