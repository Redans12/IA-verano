import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

train = pd.read_csv("./knn_cuentas_historial.csv")
caso = pd.read_csv("./knn_cuentas_caso.csv")
feats = [c for c in train.columns if c not in ("cuenta_id", "etiqueta")]

scaler = StandardScaler()
X = scaler.fit_transform(train[feats])
y = train["etiqueta"]
X_new = scaler.transform(caso[feats])

for k in (3, 5, 7):
    knn = KNeighborsClassifier(n_neighbors=k)
    scores = cross_val_score(knn, X, y, cv=5, scoring="f1_macro")
    print(k, scores.mean(), scores.std())

# TODO: entrena con tu k, predice, imprime cuenta_id + etiqueta
mejor_k = 5
knn_final = KNeighborsClassifier(n_neighbors=mejor_k)
knn_final.fit(X, y)
pred = knn_final.predict(X_new)

for cid, p in zip(caso["cuenta_id"], pred):
    print(cid, p)