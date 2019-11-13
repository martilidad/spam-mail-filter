from unittest import TestCase

from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from bayes.BayesClassifier import BayesClassifier
from core.EnronDataset import EnronDataset
from util import MailUtils, SerializationUtils


class TestBayesClassifier(TestCase):
    def setUp(self) -> None:
        data = EnronDataset().load_files()
        train_texts, test_texts, train_labels, test_labels = train_test_split(
            data.data, data.target, train_size=0.6)
        train_mails = MailUtils.strings_to_mails(train_texts)
        self.test_mails = MailUtils.strings_to_mails(test_texts)
        self.fixture = BayesClassifier(train_mails, train_labels)
        self.fixture.train()
        self.test_labels = test_labels

    def test_classify(self):
        predictions = self.fixture.classify(self.test_mails)

        accuracy = accuracy_score(self.test_labels, predictions)
        self.assertGreater(accuracy, 0.9)
        print('Accuracy score: ', accuracy)
        print('Precision score: ',
              precision_score(self.test_labels, predictions))
        print('Recall score: ', recall_score(self.test_labels, predictions))

    def test_classify_batch_train(self):
        data = EnronDataset().load_files()
        train_texts, test_texts, train_labels, test_labels = train_test_split(
            data.data, data.target, train_size=0.6)
        train_mails = MailUtils.strings_to_mails(train_texts)
        test_mails = MailUtils.strings_to_mails(test_texts)
        classifier = BayesClassifier()
        classifier.train(train_mails[:200], train_labels[:200])
        classifier.train(train_mails[200:], train_labels[200:])
        predictions = classifier.classify(test_mails)
        accuracy = accuracy_score(test_labels, predictions)
        self.assertGreater(accuracy, 0.9)
        print('Accuracy score: ', accuracy)
        print('Precision score: ', precision_score(test_labels, predictions))
        print('Recall score: ', recall_score(test_labels, predictions))

    def test_serialize_ENRON(self):
        self.fixture.serialize()
        result = BayesClassifier.deserialize()
        result.train()
        predictions = self.fixture.classify(self.test_mails)
        accuracy = accuracy_score(self.test_labels, predictions)

        result_predictions = result.classify(self.test_mails)
        result_accuracy = accuracy_score(self.test_labels, result_predictions)

        self.assertEqual(accuracy, result_accuracy)
        # Testing vocab, vector, etc. equality would take forever here.
