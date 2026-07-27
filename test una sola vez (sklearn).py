import re
import unicodedata
import nltk
from nltk.corpus import stopwords
from nltk.classify import NaiveBayesClassifier, accuracy as nltk_acc
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

nltk.download('stopwords', quiet=True)
STOPWORDS_ES = set(stopwords.words('spanish'))

def quitar_acentos(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c))

def tokens_es(texto):
    texto = texto.lower()
    texto = quitar_acentos(texto)
    texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
    palabras = texto.split()
    return [p for p in palabras if p not in STOPWORDS_ES and len(p) > 1]

def texto_limpio(s):
    return " ".join(tokens_es(s))

df = pd.read_csv("./comentarios_no_todos_votar - comentarios_youtube_voto.csv")
df["texto_proc"] = df["texto"].map(texto_limpio)
X = df["texto_proc"]
y_sent = df["sentimiento"]

Xtr, Xte, ytr, yte = train_test_split(
    X, y_sent, test_size=0.3, random_state=42, stratify=y_sent
)
print("Train:", len(Xtr), "| Test:", len(Xte))
print("Distribucion sentimiento train:\n", ytr.value_counts(normalize=True).round(3))

def doc_features(texto):
    return {f"w_{t}": True for t in tokens_es(texto)}

labeled = [(doc_features(r.texto), r.sentimiento) for r in df.itertuples()]
train_nltk, test_nltk = train_test_split(labeled, test_size=0.3, random_state=42)
clf_nb_nltk = NaiveBayesClassifier.train(train_nltk)
print("\nNLTK NaiveBayes accuracy:", round(nltk_acc(clf_nb_nltk, test_nltk), 3))
print("\nFeatures mas informativas:")
clf_nb_nltk.show_most_informative_features(12)

def evaluar(nombre, pipe, X_train, y_train, X_test, y_test):
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, pred)
    print(f"\n=== {nombre} ===  accuracy={acc:.3f}")
    print(classification_report(y_test, pred, digits=3, zero_division=0))
    print("matriz de confusion:\n", confusion_matrix(y_test, pred))
    return pipe, acc

modelos = [
    ("MultinomialNB (TF-IDF)", Pipeline([("tfidf", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", MultinomialNB())])),
    ("LogisticRegression", Pipeline([("tfidf", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", LogisticRegression(max_iter=2000, random_state=42))])),
    ("LinearSVC", Pipeline([("tfidf", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", LinearSVC(random_state=42))])),
    ("DecisionTree", Pipeline([("tfidf", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", DecisionTreeClassifier(max_depth=12, random_state=42))])),
    ("RandomForest", Pipeline([("tfidf", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", RandomForestClassifier(n_estimators=200, random_state=42))])),
    ("k-NN (k=3)", Pipeline([("tfidf", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", KNeighborsClassifier(n_neighbors=3, metric="cosine"))])),
]

resultados = []
for nombre, pipe in modelos:
    p, acc = evaluar(nombre, pipe, Xtr, ytr, Xte, yte)
    resultados.append((nombre, acc))

print("\n--- Ranking accuracy (sentimiento) ---")
for n, a in sorted(resultados, key=lambda x: -x[1]):
    print(f"  {a:.3f}  {n}")

pipes_vec = {
    "NB + Count": Pipeline([("vec", CountVectorizer(min_df=1, ngram_range=(1,2))), ("clf", MultinomialNB())]),
    "NB + TF-IDF": Pipeline([("vec", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", MultinomialNB())]),
    "LogReg + Count": Pipeline([("vec", CountVectorizer(min_df=1, ngram_range=(1,2))), ("clf", LogisticRegression(max_iter=2000, random_state=42))]),
    "LogReg + TF-IDF": Pipeline([("vec", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", LogisticRegression(max_iter=2000, random_state=42))]),
}
print("\nComparacion vectorizador (tarea sentimiento):")
for nombre, pipe in pipes_vec.items():
    pipe.fit(Xtr, ytr)
    acc = accuracy_score(yte, pipe.predict(Xte))
    print(f"  {nombre:20s}  acc={acc:.3f}")