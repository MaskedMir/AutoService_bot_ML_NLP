import joblib
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score
from config import BOT_CONFIG
import nltk

# Загружаем стоп-слова
nltk.download('stopwords')
from nltk.corpus import stopwords

# Подготовка данных
X_text = []
y = []

for intent, intent_data in BOT_CONFIG['intents'].items():
    for example in intent_data['examples']:
        X_text.append(example)
        y.append(intent)

# Инициализация векторизатора с улучшенными параметрами
stop_words = stopwords.words('russian')
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4), stop_words=stop_words)
X = vectorizer.fit_transform(X_text)

# Инициализация и обучение модели
clf = SVC(kernel='linear', probability=True)  # probability=True для возможной оценки уверенности
clf.fit(X, y)

# Кросс-валидация для оценки качества
scores = cross_val_score(clf, X, y, cv=5)
print(f"Средняя точность модели: {scores.mean():.3f} (+/- {scores.std():.3f})")

# Сохранение модели и векторизатора
joblib.dump(clf, 'intent_clf.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

def classify_intent(replica):
    # Загружаем сохраненные модель и векторизатор
    vectorizer = joblib.load('vectorizer.pkl')
    clf = joblib.load('intent_clf.pkl')
    vector = vectorizer.transform([replica])
    return clf.predict(vector)[0]