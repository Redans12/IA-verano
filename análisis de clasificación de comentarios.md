# Análisis de clasificación de sentimiento — comentarios reales de YouTube
**Analista:** [Andrés Daniel Ibarrola Origel / 22121298]

## 1. Objetivo

Comparar dos formas distintas de determinar el sentimiento de un comentario: un diccionario de palabras (sin entrenar nada) y varios modelos de machine learning entrenados, ambos aplicados sobre los mismos 30 comentarios reales que extraje del video de YouTube del podcast Leo y Nacho, donde se originó el debate del "no todos deberían votar". Cada comentario ya está etiquetado a mano por mí (negativo, neutral, positivo o sarcástico).

## 2. Parte 1: diccionario de palabras

Primero probé un enfoque sin entrenar nada, solo contando palabras positivas y negativas en cada comentario.

```python
import pandas as pd
import re
import unicodedata

df = pd.read_csv("comentarios_no_todos_votar_-_comentarios_youtube_voto.csv")

POSITIVAS = {
    "excelente", "bien", "buena", "bueno", "gracias", "genial", "increible",
    "gusto", "amor", "like", "suscrito", "correcto", "verdad", "razon",
    "libre", "libertad", "aprender", "pensar", "reflexionar", "interesante"
}

NEGATIVAS = {
    "mal", "malo", "mala", "imbeciles", "estupidos", "ignorancia", "ignorantes",
    "basura", "odio", "asco", "repugnante", "clasistas", "lamebotas",
    "mentira", "mentiroso", "engañan", "falso", "fifis", "sucios",
    "aberracion", "turbo", "valiendo", "perdidos", "dictador", "dictadura",
    "limitados", "criticar", "contradicen"
}

EMOJIS_POSITIVOS = ["❤", "🔥", "👍"]
EMOJIS_NEGATIVOS = ["🤢", "🤮", "🤡", "💩", "😂"]

def quitar_acentos(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c))

def clasificar(texto):
    texto_norm = quitar_acentos(texto.lower())
    palabras = re.findall(r'[a-z]+', texto_norm)
    pos = sum(1 for p in palabras if p in POSITIVAS)
    neg = sum(1 for p in palabras if p in NEGATIVAS)
    pos += sum(texto.count(e) for e in EMOJIS_POSITIVOS)
    neg += sum(texto.count(e) for e in EMOJIS_NEGATIVOS)
    if pos > neg:
        return "positivo"
    elif neg > pos:
        return "negativo"
    else:
        return "neutro"

df["sentimiento_diccionario"] = df["texto"].apply(clasificar)
print(df["sentimiento_diccionario"].value_counts())
```

**Resultado:** 13 negativo, 12 neutro, 5 positivo.

Revisando algunos casos a mano encontré varios errores claros del método:
- El comentario de @orlandolopez7813 ("Gracias a amlo a shembau y alas mañaneras ya no engañas a nadie") salió como positivo solo porque tiene la palabra "gracias", pero en realidad es sarcasmo, es una crítica.
- El comentario de @SonidoYerpeliz salió con un score de 35 en negativo, pero eso es solo porque repitió el emoji 😂 más de 30 veces, no porque el comentario en sí sea 35 veces más negativo que los demás.
- @lizethfigueroa2767 escribió "El pueblo tiene el poder" y salió neutro, cuando en el contexto de la discusión es un comentario de tono confrontativo, pero como ninguna palabra suelta está en mis listas, no lo detecta.

Esto pasa porque el diccionario solo cuenta palabras sueltas, no entiende sarcasmo, ni contexto, ni que una palabra "positiva" puede estar dentro de una crítica.

## 3. Parte 2: modelos de machine learning

Usando la etiqueta que puse a mano (`sentimiento`), entrené varios modelos con TF-IDF sobre los mismos 30 comentarios.

```python
import re
import unicodedata
import nltk
from nltk.corpus import stopwords
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

df = pd.read_csv("comentarios_no_todos_votar_-_comentarios_youtube_voto.csv")
df["texto_proc"] = df["texto"].map(texto_limpio)
X = df["texto_proc"]
y_sent = df["sentimiento"]

Xtr, Xte, ytr, yte = train_test_split(X, y_sent, test_size=0.3, random_state=42, stratify=y_sent)

modelos = [
    ("MultinomialNB (TF-IDF)", Pipeline([("tfidf", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", MultinomialNB())])),
    ("LogisticRegression", Pipeline([("tfidf", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", LogisticRegression(max_iter=2000, random_state=42))])),
    ("LinearSVC", Pipeline([("tfidf", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", LinearSVC(random_state=42))])),
    ("DecisionTree", Pipeline([("tfidf", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", DecisionTreeClassifier(max_depth=12, random_state=42))])),
    ("RandomForest", Pipeline([("tfidf", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", RandomForestClassifier(n_estimators=200, random_state=42))])),
    ("k-NN (k=3)", Pipeline([("tfidf", TfidfVectorizer(min_df=1, ngram_range=(1,2))), ("clf", KNeighborsClassifier(n_neighbors=3, metric="cosine"))])),
]

for nombre, pipe in modelos:
    pipe.fit(Xtr, ytr)
    pred = pipe.predict(Xte)
    acc = accuracy_score(yte, pred)
    print(nombre, round(acc, 3))
    print(classification_report(yte, pred, digits=3, zero_division=0))
    print(confusion_matrix(yte, pred))
```

**Resultado (21 comentarios de entrenamiento, 9 de prueba, por lo chico del dataset):**

| Modelo | Accuracy |
|---|---|
| MultinomialNB (TF-IDF) | 0.667 |
| LogisticRegression | 0.667 |
| LinearSVC | 0.667 |
| RandomForest | 0.667 |
| DecisionTree | 0.556 |
| k-NN (k=3) | 0.556 |

A simple vista el 0.667 se ve bien, pero revisando la matriz de confusión de LogisticRegression:

```
[[6 0 0 0]   negativo real -> predijo negativo (bien)
 [1 0 0 0]   neutral real  -> predijo negativo (mal)
 [1 0 0 0]   positivo real -> predijo negativo (mal)
 [1 0 0 0]]  sarcástico real -> predijo negativo (mal)
```

El modelo está prediciendo negativo casi siempre, porque el 63% de mis 30 comentarios son negativos. Entonces acierta bastante solo por predecir la clase que más se repite, sin distinguir de verdad entre neutral, positivo o sarcástico.

## 4. Comparación

| Enfoque | Resultado | Qué está pasando en realidad |
|---|---|---|
| Diccionario de palabras | 13 negativo, 12 neutro, 5 positivo (sin accuracy porque no hay comparación con etiqueta) | Falla con sarcasmo, contexto y emojis repetidos |
| ML (6 modelos) | 0.667 el mejor | Predice casi siempre la clase mayoritaria (negativo), no distingue bien las otras clases |

## 5. Conclusión

Ninguno de los dos enfoques logra clasificar bien el sentimiento de estos comentarios reales. El diccionario falla porque solo cuenta palabras sueltas sin entender sarcasmo ni contexto, como se vio con los casos de @orlandolopez7813 y @lizethfigueroa2767. Los modelos de ML, aunque llegan a 0.667 de accuracy, en realidad están haciendo trampa: como el 63% de mis comentarios son negativos, el modelo aprende el atajo de predecir siempre esa clase y así ya acierta bastante, sin distinguir de verdad entre neutral, positivo o sarcástico, que es justo el mismo problema que vimos con la variable `abandona` en la Misión 2 de las 4 misiones, donde un accuracy alto tampoco significaba que el modelo fuera bueno.

Con solo 30 comentarios y desbalanceados entre clases, ninguno de los dos métodos tiene suficiente información para aprender un patrón real de sentimiento. Haría falta un dataset real mucho más grande y balanceado entre las categorías para que un modelo de verdad pueda distinguir entre negativo, neutral, positivo y sarcástico de forma confiable.