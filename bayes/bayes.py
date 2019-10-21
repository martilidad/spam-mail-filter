from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from util.EnronDataset import EnronDataset
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score

data = EnronDataset().load_files()
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, random_state=1)

#decode_error replace needed because of weird unicode chars
cv = CountVectorizer(strip_accents='unicode', token_pattern=u'(?ui)\\b\\w*[a-z]+\\w*\\b',
                     lowercase=True, stop_words='english', decode_error='replace')
X_train_cv = cv.fit_transform(X_train)
X_test_cv = cv.transform(X_test)


naive_bayes = MultinomialNB()
naive_bayes.fit(X_train_cv, y_train)
predictions = naive_bayes.predict(X_test_cv)
print('Accuracy score: ', accuracy_score(y_test, predictions))
print('Precision score: ', precision_score(y_test, predictions))
print('Recall score: ', recall_score(y_test, predictions))
