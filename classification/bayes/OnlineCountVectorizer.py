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

    def update_vocabulary(self, raw_documents: [str]):
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
