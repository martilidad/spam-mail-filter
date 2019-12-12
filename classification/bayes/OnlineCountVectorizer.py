from typing import List

from scipy import sparse
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import CountVectorizer


class OnlineCountVectorizer(CountVectorizer):
    def __init__(self, vocabulary=None):
        super().__init__(strip_accents='unicode',
                         token_pattern=u'(?ui)\\b\\w*[a-z]+\\w*\\b',
                         lowercase=True,
                         stop_words='english',
                         decode_error='replace',
                         vocabulary=vocabulary)

    def fit_transform(self, raw_documents, y=None):
        self.update_vocabulary(raw_documents)
        return self.transform(raw_documents)

    def update_vocabulary(self, raw_documents: List[str]):
        # retrieve new vocab
        new_vectorizer = CountVectorizer()
        new_vectorizer.fit_transform(raw_documents)
        new_vocab = new_vectorizer.vocabulary_

        # merge vocabularies
        curr_vocab = self.vocabulary
        if curr_vocab is None:
            curr_vocab = new_vocab
        else:
            i = len(curr_vocab)
            for key in new_vocab.keys():
                if key not in curr_vocab.keys():
                    curr_vocab[key] = i
                    i += 1
        # update vectorizer
        self.vocabulary = curr_vocab
        if hasattr(self, 'vocabulary_'):
            delattr(self, 'vocabulary_')

    def combine(self, m1: csr_matrix, m2: csr_matrix) -> csr_matrix:
        """
        Combines two vectorized matrices to one complying to current vocabulary
        """
        m2.resize(m2.shape[0], len(self.vocabulary))
        m1.resize(m1.shape[0], len(self.vocabulary))
        return sparse.vstack((m1, m2))
