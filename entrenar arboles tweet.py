import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text

hist = pd.read_csv("./arbol_amplificacion_historial.csv")
caso = pd.read_csv("./arbol_escenarios_caso.csv")

feats = [c for c in hist.columns if c not in ("caso_id", "accion")]
X = hist[feats]
y = hist["accion"]

clf = DecisionTreeClassifier(max_depth=4, random_state=42)
clf.fit(X, y)

print("=== Reglas del árbol ===")
print(export_text(clf, feature_names=feats))

X_new = caso[feats]
pred = clf.predict(X_new)
print("=== Predicciones ===")
for cid, p in zip(caso["caso_id"], pred):
    print(f"{cid}: {p}")