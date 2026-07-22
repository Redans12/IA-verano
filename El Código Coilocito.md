# El Código Coilocito — Informe forense
**Analista:** [Andrés Daniel Ibarrola Origel / 22121298]

## ACTO I — Matching con similitud coseno

**Código utilizado:**

```python
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("./similitud_tf_documentos.csv")

feats = [c for c in df.columns if c not in ("documento", "tipo")]

perfiles = df[df["tipo"] == "perfil"].set_index("documento")[feats]
pistas = df[df["tipo"] == "pista"].set_index("documento")[feats]

sim = pd.DataFrame(
    cosine_similarity(pistas.values, perfiles.values),
    index=pistas.index, columns=perfiles.index,
)

print(sim)
print("mejor match por pista:")
for pista in sim.index:
    mejor = sim.loc[pista].idxmax()
    valor = sim.loc[pista].max()
    print(f"{pista} -> {mejor} ({valor:.3f})")
```

**Entrega Acto I**

| Pista | Perfil más similar | Coseno (aprox.) |
|---|---|---|
| A (bitacora_red) | perfil_elena | 0.789 |
| B (correo_interno) | perfil_valeriano | 0.925 |
| C (fragmento_emacs) | perfil_hacker_interno | 0.935 |
| D (commit_gitlab) | perfil_elena | 0.970 |

**Hipótesis preliminar:**
Con el coseno, dos de las cuatro pistas apuntan directamente a Elena: la pista D (commit_gitlab) es la más alta de toda la matriz con 0.970, y la pista A (bitacora_red) también le pega a ella con 0.789. Esto coincide con lo que ya vimos en pista_codigo_borrado.py, donde el commit del hotfix que exportó los pesos del modelo a un USB "temporal" está firmado por e.fullstack, que es justo el apodo de Elena en el briefing ("Elena «La Full-Stack»"). La pista C (fragmento_emacs) sí le pega fuerte al hacker interno (0.935), pero según pista_laboratorio.md ese .emacs.d apareció en el home de un usuario temporal dev_elena y el propio documento lo marca como "posible señuelo", entonces no lo tomaría como evidencia sólida todavía, podría ser algo puesto ahí a propósito para desviar la sospecha hacia el hacker interno. La pista B (correo_interno) sí le pega fuerte a Valeriano (0.925), lo cual coincide con el borrador de correo quejándose del "retroceso científico" que se encontró en su papelera, pero por ahora solo parece un motivo, no evidencia de que él haya ejecutado el sabotaje. Con esto, mi hipótesis preliminar es que Elena es la principal sospechosa, aunque todavía faltan los siguientes actos para confirmarlo con más evidencia.

---

## ACTO II — Tipo de ataque con k-NN

**Código utilizado:**

```python
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

train = pd.read_csv("./knn_historial_ataques.csv")
caso = pd.read_csv("./knn_caso_arispe.csv")

feats = [c for c in train.columns if c not in ("caso_id", "etiqueta_ataque")]
X_raw = train[feats]
y = train["etiqueta_ataque"]
X_new_raw = caso[feats]

scaler = StandardScaler()
X = scaler.fit_transform(X_raw)
X_new = scaler.transform(X_new_raw)

for k in (3, 5, 7):
    knn = KNeighborsClassifier(n_neighbors=k)
    scores = cross_val_score(knn, X, y, cv=5, scoring="f1_macro")
    print(k, scores.mean(), scores.std())

modelo = KNeighborsClassifier(n_neighbors=5)
modelo.fit(X, y)
pred = modelo.predict(X_new)
print("prediccion:", pred)
```

Usé StandardScaler porque las columnas del dataset están en escalas muy distintas entre sí, por ejemplo archivos_copiados_mb llega hasta los 2000-2700, mientras que uso_vpn solo vale 0 o 1. Si no se escalan, la columna con números más grandes (como archivos_copiados_mb) dominaría el cálculo de distancia de k-NN aunque no sea la variable más importante, dejando a las demás columnas casi sin peso en la decisión.

**Entrega Acto II**

| | |
|---|---|
| k elegido | 5 |
| F1 macro (CV) | 0.9916 |
| Predicción caso Arispe | robo_sigiloso_cuello_blanco |

**Trampa (sin scaler):** corrí lo mismo sin StandardScaler y la predicción no cambió (sigue dando robo_sigiloso_cuello_blanco), pero el F1 macro sí bajó de 0.9916 a 0.9164 con k=5. Esto significa que aunque en este caso particular la predicción final fue la misma, el modelo sin escalar es menos confiable en general (se equivoca más seguido en la validación cruzada), así que igual conviene usar el scaler aunque el resultado puntual no haya cambiado.

**Relación con Acto I:**
El resultado de robo_sigiloso_cuello_blanco encaja con mi hipótesis de Elena del Acto I. Un "robo sigiloso de cuello blanco" suena a alguien con acceso legítimo que actúa con cuidado, no como un ataque de fuerza bruta corporativa ni un sabotaje descuidado, y esto es consistente con el perfil de Elena como contratista con acceso a Django/PostgreSQL/VPN/Docker, herramientas que sugieren que sabe moverse dentro del sistema sin necesidad de forzar nada. Además, el caso Arispe tiene uso_vpn=1, y en pista_laboratorio.md se menciona que el DROP SCHEMA se ejecutó desde una sesión SSH con salto por VPN corporativa externa, lo cual también apunta a alguien con acceso autorizado y no a un intento de fuerza bruta desde afuera.

---

## ACTO III — Fuga con árbol de decisión

**Código utilizado:**

```python
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text

hist = pd.read_csv("./arbol_fugas_historial.csv")
esc_culpable = pd.read_csv("./arbol_escenario_culpable.csv")
esc_valeriano = pd.read_csv("./arbol_escenario_valeriano.csv")

feats = [c for c in hist.columns if c not in ("fuga_id", "ruta_elegida")]
X = hist[feats]
y = hist["ruta_elegida"]

clf = DecisionTreeClassifier(max_depth=4, random_state=42)
clf.fit(X, y)

print(export_text(clf, feature_names=feats))

pred_culpable = clf.predict(esc_culpable[feats])
pred_valeriano = clf.predict(esc_valeriano[feats])
print("Ruta culpable:", pred_culpable)
print("Ruta contrafactual Valeriano:", pred_valeriano)
```

**Reglas principales del árbol:**

```
|--- fondos_corporativos <= 0.50
|   |--- conoce_laberinto_campus <= 0.50
|   |   |--- acceso_red_oscura <= 0.50
|   |   |   |--- class: puerto_carga
|   |   |--- acceso_red_oscura >  0.50
|   |   |   |--- class: tren_nocturno
|   |--- conoce_laberinto_campus >  0.50
|   |   |--- class: escondite_instituto
|--- fondos_corporativos >  0.50
|   |--- alerta_aeropuerto <= 0.50
|   |   |--- class: vuelo_internacional
|   |--- alerta_aeropuerto >  0.50
|   |   |--- pasaporte_falso <= 0.50
|   |   |   |--- class: puerto_carga
|   |   |--- pasaporte_falso >  0.50
|   |   |   |--- class: frontera_terrestre
```

La variable más importante del árbol (la raíz) es fondos_corporativos, o sea que lo primero que separa las rutas de fuga es si la persona tiene o no respaldo económico de una empresa detrás.

**Entrega Acto III**

| | |
|---|---|
| Culpable que acusas | Elena |
| Ruta predicha | vuelo_internacional |
| Contrafactual Valeriano → ruta | escondite_instituto |

**Orden de interceptación:**
Con base en el árbol, si Elena es la culpable (fondos_corporativos=1, alerta_aeropuerto=0), la ruta predicha es vuelo_internacional, así que la prioridad sería alertar de inmediato a control migratorio y aeropuertos cercanos antes de que aborde algún vuelo, ya que el árbol indica que sin alerta de aeropuerto activada, alguien con fondos corporativos casi siempre elige esa ruta.

**Contrafactual:** si en cambio el culpable fuera Valeriano (sin fondos corporativos pero conociendo el laberinto del campus), el árbol predice escondite_instituto, es decir, una fuga completamente distinta y mucho más cercana, dentro de las propias instalaciones. Esto sí cambiaría la persecución por completo: en vez de vigilar aeropuertos, habría que cerrar y revisar el campus mismo. El hecho de que ambos escenarios den rutas tan diferentes confirma que la variable fondos_corporativos es decisiva para saber a dónde buscar.

---

## ACTO EXTRA — Regresión lineal

**Código utilizado:**

```python
import pandas as pd
from sklearn.linear_model import LinearRegression

df = pd.read_csv("./regresion_benchmark_coilocitos.csv")

for metodo, g in df.groupby("metodo"):
    X = g[["n_celulas"]]
    y = g["tiempo_inferencia_s"]
    reg = LinearRegression()
    reg.fit(X, y)
    t10k = reg.predict([[10000]])[0]
    print(metodo, reg.intercept_, reg.coef_[0], t10k, reg.score(X, y))
```

**Entrega Extra**

| Método | β0 | β1 | t@10k (s) |
|---|---|---|---|
| sift_surf_clasico | 1.767 | 0.01199 | 121.69 |
| cnn_profunda | 11.977 | 0.08506 | 862.55 |

**Interpretación:**
El coeficiente β1 de SIFT/SURF (0.012) es mucho más chico que el de CNN (0.085), es decir, por cada célula adicional, el tiempo de inferencia de CNN crece casi 7 veces más rápido que el de SIFT/SURF. A 10,000 células, SIFT/SURF tardaría aproximadamente 121.7 segundos contra 862.6 segundos de CNN, una diferencia enorme. Ambos ajustes tienen un R² muy alto (0.9994 y 0.9996), lo cual significa que la relación lineal explica casi toda la variación de los datos dentro del rango que se midió (200 a 5000 células).

Aun así, hay que tener cuidado al extrapolar a 10,000 células, porque los datos reales solo llegan hasta 5000, o sea que estamos prediciendo el doble del rango que en verdad se midió. No hay garantía de que la relación siga siendo perfectamente lineal fuera de ese rango; en la práctica podría haber otros factores (como límites de memoria o RAM) que cambien el comportamiento a volúmenes tan grandes.

Esto conecta con un posible móvil: el algoritmo de SIFT/SURF del Dr. Arispe es muchísimo más rápido y liviano que una CNN, lo cual encaja con la nota que se encontró en pista_codigo_borrado.py ("no migrar a CNN — presupuesto hospitales rurales"). Un algoritmo así de eficiente, que permite equipos médicos baratos, tiene valor comercial real, lo que refuerza el motivo de robarlo para patentarlo antes que Arispe, en vez de que quede como conocimiento abierto.

---

## Veredicto final

¿A quién acusas y por qué? (coherencia entre actos):
Acuso a Elena «La Full-Stack» como la responsable del sabotaje y robo del algoritmo de coilocitos. La coherencia entre los cuatro actos apunta consistentemente hacia ella: en el Acto I, dos de las cuatro pistas (la más fuerte de toda la matriz, con 0.970, y otra con 0.789) apuntan a su perfil, y esto se refuerza con el commit de pista_codigo_borrado.py firmado por e.fullstack, que exportó los pesos del modelo a un USB "temporal" 48 horas antes del robo. En el Acto II, el tipo de ataque que predice el k-NN para el caso Arispe es robo_sigiloso_cuello_blanco, que encaja con el perfil de alguien con acceso legítimo (VPN, contratista) actuando con cuidado, no con fuerza bruta. En el Acto III, el árbol predice que su ruta de fuga sería vuelo_internacional, dado que cuenta con fondos corporativos, lo cual da una pista concreta de dónde buscarla. Y en el Acto Extra, el móvil económico queda reforzado al ver que el algoritmo de SIFT/SURF de Arispe es mucho más eficiente que una CNN, lo que lo vuelve valioso para patentar y cerrar, en vez de dejarlo abierto para hospitales rurales.

¿Qué pista o resultado podría estar engañándote?:
La pista que más podría estar engañándome es la C (fragmento_emacs), que apunta al hacker interno con el coseno más alto de toda la matriz (0.935). Sin embargo, pista_laboratorio.md señala directamente que ese .emacs.d apareció en el home de un usuario temporal llamado dev_elena, casi vacío, y lo describe como "posible señuelo". Esto podría ser justamente un intento de Elena de desviar la sospecha hacia el hacker interno, dejando rastros falsos de Emacs en una cuenta temporal para que la investigación se enfoque en el sospechoso equivocado.

¿Qué harías si tu k-NN y tu coseno no coincidieran?:
Si mi k-NN y mi coseno no hubieran coincidido (por ejemplo, si el k-NN hubiera predicho fuerza_bruta_corporativa en vez de robo_sigiloso_cuello_blanco), habría necesitado buscar una tercera fuente de evidencia antes de acusar, en vez de confiar en una sola señal. En este caso no fue necesario porque ambos análisis (coseno del Acto I y k-NN del Acto II) apuntaron consistentemente hacia el mismo perfil, lo cual me da mayor confianza en el veredicto final.