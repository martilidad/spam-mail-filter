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
        base_vocab = self.vocabulary
        self.__init__()
        try:
            super().fit_transform(raw_documents)
        except ValueError:
            return
        vocab = self.vocabulary_
        if base_vocab is None:
            self.__init__(vocab)
            return
        # merge vocabularies
        i = len(base_vocab)
        for key in vocab.keys():
            if key not in base_vocab.keys():
                base_vocab[key] = i
                i += 1
        # update vectorizer
        self.__init__(base_vocab)

    def combine(self, m1: csr_matrix, m2: csr_matrix) -> csr_matrix:
        """
        Combines two vectorized matrices to one complying to current vocabulary
        """
        m2.resize(m2.shape[0], len(self.vocabulary))
        m1.resize(m1.shape[0], len(self.vocabulary))
        return sparse.vstack((m1, m2))
