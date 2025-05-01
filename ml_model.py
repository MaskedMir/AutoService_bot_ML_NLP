from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from config import BOT_CONFIG

X_text = []
y = []

for intent, intent_data in BOT_CONFIG['intents'].items():
    for example in intent_data['examples']:
        X_text.append(example)
        y.append(intent)

vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 3))
X = vectorizer.fit_transform(X_text)

clf = LinearSVC()
clf.fit(X, y)

def classify_intent(replica):
    vector = vectorizer.transform([replica])
    return clf.predict(vector)[0]
