# Dispersión de Rumores — Informe ExamenFiltrado
**Analista:** [Andrés Daniel Ibarrola Origel / 22121298]

## Misión 0 — Aclara el problema

**¿Qué es el origen del rumor?**
Es el primer tweet (el de menor minuto) que introduce el contenido específico del rumor, antes de que cualquier otra cuenta lo replique o lo comente. No se identifica por el texto que dice (porque las copias dicen casi lo mismo), sino por ser temporalmente el primero en publicarlo.

**¿Qué es la dispersión?**
Es cómo se va expandiendo el rumor a partir del origen: primero las cuentas que copian el mensaje casi textual (como @info_rapida_01...@viral_edu_05), luego los que lo comentan o amplifican con sus propias palabras (como @diego_campus, @vale_ia), y finalmente las reacciones como el desmentido (@omar_verifica, @rectoria_iti). Es el proceso completo de cómo un solo tweet se convierte en muchos tweets relacionados, no solo el conteo final.

**¿Por qué un coseno alto no basta para saber quién empezó?**
Porque el coseno solo mide qué tan parecido es el contenido de dos tweets, no en qué momento se publicó cada uno. Si dos tweets son casi idénticos (coseno cercano a 1), eso nos dice que probablemente hablan del mismo rumor o que uno copió al otro, pero no nos dice cuál de los dos se escribió primero. Para saber eso necesitamos el dato del minuto de publicación (columna `minuto` en `timeline_tweets.csv`), no solo la similitud del texto.

**¿Qué peligro hay si solo miras "quién tiene más seguidores"?**
El peligro es confundir popularidad con fiabilidad o con ser el origen del rumor, una cuenta con muchos seguidores no necesariamente fue la que empezó el rumor, ni tampoco significa que lo que dice sea verdad; de hecho, en este caso @rectoria_iti es quien desmiente el rumor, no quien lo origina. Entonces si solo nos guiáramos por el número de seguidores, caeríamos en un error señalando una cuenta como el origen aunque esta sea la que lo desmiente.

---

## Misión 1 — EDA: ¿cuándo explotó la conversación?

| Pregunta | Respuesta |
|---|---|
| Ventana crítica (min ini–fin) | 30–40 |
| Tweets en esa ventana | 6 |
| pct_cuentas_nuevas | 0.67 |
| Interpretación en 3 líneas | En la ventana de 30-40 min es donde explota la conversación, con 6 tweets. Al observar la columna de pct_cuentas_nuevas, en esta fila aumenta drásticamente de 0 a 0.67, con esto podemos pensar que los que tweetean sobre esto son bots o una "red automatizada". |

---

## Misión 2 — Coseno: ¿mismo rumor o copia?

**Código utilizado:**

```python
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("./similitud_tweets_tf.csv")
feats = [c for c in df.columns if c not in ("documento", "tipo")]

semillas = df[df["tipo"] == "semilla"].set_index("documento")[feats]
tweets = df[df["tipo"] == "tweet"].set_index("documento")[feats]

sim_sem = pd.DataFrame(
    cosine_similarity(tweets.values, semillas.values),
    index=tweets.index, columns=semillas.index,
)
sim_tw = pd.DataFrame(
    cosine_similarity(tweets.values),
    index=tweets.index, columns=tweets.index,
)

print(sim_sem.round(3))
# TODO: imprime pares i<j con sim_tw >= 0.90
tw_list = list(tweets.index)
for i in range(len(tw_list)):
    for j in range(i + 1, len(tw_list)):
        v = sim_tw.iloc[i, j]
        if v >= 0.90:
            print(f"{tw_list[i]} -- {tw_list[j]} : {v:.3f}")
```

**Tweet → Semilla más cercana → Coseno**

| Tweet | Semilla más cercana | Coseno |
|---|---|---|
| tw_origen_luna | semilla_rumor_examen | 0.976 |
| tw_bot_01 | semilla_rumor_examen | 0.967 |
| tw_bot_02 | semilla_rumor_examen | 0.951 |
| tw_bot_03 | semilla_rumor_examen | 0.925 |
| tw_bot_04 | semilla_rumor_examen | 0.891 |
| tw_bot_05 | semilla_rumor_examen | 0.908 |
| tw_amplifica_diego | semilla_rumor_examen | 0.814 |
| tw_amplifica_vale | semilla_rumor_examen | 0.644 |
| tw_comedor_sofia | semilla_rumor_comedor | 0.982 |
| tw_comedor_eco | semilla_rumor_comedor | 0.906 |
| tw_ruido_becas | semilla_ruido_becas | 0.993 |
| tw_ruido_beca2 | semilla_ruido_becas | 0.869 |
| tw_desmiente_omar | semilla_desmentido | 0.982 |
| tw_desmiente_rectoria | semilla_desmentido | 0.913 |

**Pares casi-clon (≥ 0.90):**

| Par | Coseno |
|---|---|
| tw_origen_luna -- tw_bot_01 | 0.948 |
| tw_origen_luna -- tw_bot_02 | 0.901 |
| tw_bot_01 -- tw_bot_02 | 0.984 |
| tw_bot_01 -- tw_bot_03 | 0.944 |
| tw_bot_01 -- tw_bot_04 | 0.923 |
| tw_bot_01 -- tw_bot_05 | 0.930 |
| tw_bot_02 -- tw_bot_03 | 0.974 |
| tw_bot_02 -- tw_bot_04 | 0.968 |
| tw_bot_02 -- tw_bot_05 | 0.963 |
| tw_bot_03 -- tw_bot_04 | 0.973 |
| tw_bot_03 -- tw_bot_05 | 0.962 |
| tw_bot_04 -- tw_bot_05 | 0.963 |
| tw_amplifica_diego -- tw_amplifica_vale | 0.932 |

**¿Qué tweets son otro tema (comedor/becas) y no el rumor de examen?**
Los tweets tw_comedor_sofia y tw_comedor_eco tienen su semilla más cercana en semilla_rumor_comedor (0.982 y 0.906), y los tweets tw_ruido_becas y tw_ruido_beca2 tienen su semilla más cercana en semilla_ruido_becas (0.993 y 0.869). Estos 4 tweets no hablan del rumor del examen, sino de otros temas (el comedor y las becas), y se puede confirmar porque su coseno contra semilla_rumor_examen es muy bajo (todos por debajo de 0.18), mientras que su coseno contra su propia semilla es mucho más alto.

---

## Misión 3 — Timeline + cascada: ¿quién primero y cómo se repartió?

| Rol que propones | Usuario | Minuto | Evidencia (1 frase) |
|---|---|---|---|
| Origen del examen | @luna_mx | 12 | Tiene el minuto más bajo de todas las cuentas del tema examen y una cuenta con 1200 días de antigüedad, consistente con ser una cuenta humana real y no creada para el rumor |
| Amplificador humano | @diego_campus / @vale_ia | 28 / 35 | Su enlace es tipo cita_comenta y tienen cuentas viejas (800 y 950 días), lo que sugiere que comentan con sus propias palabras en vez de copiar el texto original |
| Red de copias (lista) | @info_rapida_01, @alertas_edu_02, @noticias_ya_03, @flash_campus_04, @viral_edu_05 | 31–37 | Todos tienen enlace tipo copia_texto y cuentas de 1 a 4 días de antigüedad, publicando casi al mismo tiempo (31-37 min), lo que significa que son bots creados para el rumor |
| Desmentido | @omar_verifica | 45 | Su enlace es tipo desmiente hacia @luna_mx, y @rectoria_iti lo refuerza en el minuto 52 con tipo_enlace refuerza_desmentido |

**Cascada:**

```
@luna_mx  --copia_texto-->  @info_rapida_01
@luna_mx  --copia_texto-->  @alertas_edu_02
@luna_mx  --cita_comenta-->  @diego_campus
@luna_mx  --desmiente-->  @omar_verifica

@info_rapida_01  --copia_texto-->  @noticias_ya_03
@alertas_edu_02  --copia_texto-->  @flash_campus_04
@noticias_ya_03  --copia_texto-->  @viral_edu_05
@diego_campus  --cita_comenta-->  @vale_ia
@omar_verifica  --refuerza_desmentido-->  @rectoria_iti
```

**Pregunta de pensamiento: ¿por qué "más likes" o "más seguidores" no define automáticamente al originador?**
Porque los likes y tener muchos seguidores no es ningún indicador real o seguro de que la cuenta es un originador, por ejemplo, @rectoria_iti tiene 5000 seguidores, entonces si solo nos basáramos en este número, podríamos pensar que es una cuenta que originó el rumor, sin embargo, gracias a otros datos sabemos que es una cuenta que lo desmintió. Y los likes tampoco son indicadores, ya que los bots son los que tienen mayor número de likes porque para eso están diseñados, esto no quiere decir que hayan sido los primeros en publicar el rumor.

---

## Misión 4 — k-NN: ¿bot o humano?

**Código utilizado:**

```python
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

mejor_k = 5
knn_final = KNeighborsClassifier(n_neighbors=mejor_k)
knn_final.fit(X, y)
pred = knn_final.predict(X_new)

for cid, p in zip(caso["cuenta_id"], pred):
    print(cid, p)
```

| Cuenta | Predicción | ¿Cuadra con M2/M3? |
|---|---|---|
| @info_rapida_01 | bot | Sí, coincide con M2 (coseno casi idéntico a la semilla y a otros bots) y M3 (red de copias) |
| @alertas_edu_02 | bot | Sí, mismo patrón que los demás bots identificados en M2/M3 |
| @noticias_ya_03 | bot | Sí, coincide con la red de copias identificada en M3 |
| @flash_campus_04 | bot | Sí, coincide con la red de copias identificada en M3 |
| @viral_edu_05 | bot | Sí, coincide con la red de copias identificada en M3 |
| @luna_mx | humano | Sí, coincide con M3, donde se identificó como el origen (cuenta vieja, minuto más bajo) |
| @diego_campus | humano | Sí, coincide con M3, identificado como amplificador humano (cita_comenta, cuenta vieja) |
| @vale_ia | humano | Sí, coincide con M3, identificado como amplificador humano junto con Diego |
| @omar_verifica | humano | Sí, coincide con M3, identificado como quien desmiente el rumor |
| @sofia_comedor | humano | No estaba en el análisis de M2/M3 (es del tema comedor, no del rumor de examen), pero es consistente que salga humano |
| @rectoria_iti | humano | Sí, coincide con M3, identificado como quien refuerza el desmentido |

**Si hubiera conflicto entre coseno y k-NN, ¿qué harías?**
Si hubiera conflicto entre coseno y k-NN para una misma cuenta (por ejemplo, coseno dice que su texto es casi idéntico a un bot, pero k-NN la clasifica como humano por su comportamiento), significaría que alguna de las dos señales no está capturando bien la realidad de esa cuenta en particular — un humano podría coincidir en palabras por casualidad, o un bot podría tener métricas de comportamiento que parezcan humanas. En ese caso, en vez de confiar ciegamente en una sola señal, revisaría una tercera fuente: cascada_enlaces.csv, para ver si esa cuenta aparece con tipo_enlace = copia_texto hacia otra cuenta del rumor. Si sí copia texto de forma directa, eso reforzaría la señal del coseno; si no aparece copiando a nadie, reforzaría la señal de k-NN. Con dos de tres fuentes de acuerdo, tendría más confianza en la conclusión final.

---

## Misión 5 — Árbol: ¿amplifica o contrarresta?

**Código utilizado:**

```python
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
```

| Escenario | Acción predicha |
|---|---|
| redbots | amplifica_en_masa |
| diego | amplifica_influencer |
| vale | amplifica_influencer |
| omar | contrarresta |
| sofiacomedor | ignora |

**Acción prioritaria para el campus + justificación:**
La acción prioritaria para el campus sería impulsar y acelerar el desmentido, ya que la raíz del árbol nos lo indica: la primera y más importante pregunta que hace el modelo para decidir la acción es si ya_desmintio, por sobre si es bot, seguidores, si publica de noche, etc. Entonces según el historial, el factor que más cambia el comportamiento de las cuentas es que exista un desmentido activo.

---

## Misión 6 — Regresión: ¿qué mueve el alcance?

**Código utilizado:**
```python
import pandas as pd
from sklearn.linear_model import LinearRegression

df = pd.read_csv("./regresion_alcance_rumor.csv")
feats = ["minutos_desde_origen", "bots_activos", "desmentidos_activos"]
X = df[feats]
y = df["alcance_cuentas"]

reg = LinearRegression()
reg.fit(X, y)

print("Beta0 (intercepto):", round(reg.intercept_, 2))
for f, coef in zip(feats, reg.coef_):
    print(f"Beta {f}:", round(coef, 2))

print("R^2:", round(reg.score(X, y), 4))

escenarios = pd.DataFrame({
    "minutos_desde_origen": [60, 60, 60],
    "bots_activos": [10, 10, 0],
    "desmentidos_activos": [0, 2, 2],
})
preds = reg.predict(escenarios)
for i, p in zip(["A", "B", "C"], preds):
    print(f"Escenario {i}: alcance predicho = {p:.1f}")
```

| Coeficiente | Valor aprox. | Significado en una frase |
|---|---|---|
| β0 | 19.86 | Es el alcance esperado cuando no hay bots, no hay desmentidos y minutos_desde_origen es 0 (el punto de partida base) |
| βminutos | 1.82 | Por cada minuto adicional desde el origen, el alcance sube en promedio 1.82 cuentas |
| βbots | 14.36 | Por cada bot activo adicional, el alcance sube en promedio 14.36 cuentas (efecto positivo, amplifica la dispersión) |
| βdesmentidos | -17.37 | Por cada desmentido activo adicional, el alcance baja en promedio 17.37 cuentas (efecto negativo, frena la dispersión) |

| Escenario | minutos | bots | desmentidos | alcance predicho |
|---|---|---|---|---|
| A | 60 | 10 | 0 | 272.8 |
| B | 60 | 10 | 2 | 238.1 |
| C | 60 | 0 | 2 | 94.5 |

**¿Qué escenario conviene más al campus y por qué?**
El C es el mejor escenario porque tiene el alcance más bajo, esto es porque no tiene bots activos, por lo tanto no suma nada por el coeficiente β_bots, y aparte ya tiene 2 desmentidos activos que le ayudan a restar por el coeficiente β_desmentidos. El conjunto de todo esto nos dice que tiene el menor alcance del rumor, que es justamente lo que busca el campus.

---

## Misión 7 — Informe final de dispersión

El rumor del examen filtrado lo originó @luna_mx, ya que en la Misión 3 vimos que es la cuenta con el minuto más bajo de todas las relacionadas con el tema (minuto 12), y con una antigüedad de 1200 días, lo cual es consistente con una cuenta humana real y no una creada para el rumor.

A partir de ahí, el rumor se dispersó en dos frentes distintos. Por un lado, una red de cinco cuentas (@info_rapida_01, @alertas_edu_02, @noticias_ya_03, @flash_campus_04, @viral_edu_05) copiaron el texto casi de forma idéntica, con cosenos de 0.89 a 0.98 tanto contra la semilla del rumor como entre ellas mismas (Misión 2), y todas publicaron en una ventana muy corta de tiempo (31-37 minutos), lo cual coincide con el pico de cuentas nuevas que detectamos en la Misión 1 (67% de cuentas nuevas justo en la ventana de 30-40 minutos). Por otro lado, @diego_campus y @vale_ia amplificaron el rumor pero comentándolo con sus propias palabras, ya que su coseno contra la semilla es más bajo (0.81 y 0.64) pero entre ellos es alto (0.93), en vez de copiar el texto original tal cual.

Según el modelo k-NN que entrenamos con las cuentas históricas etiquetadas (Misión 4), las cinco cuentas de la red de copias se clasifican como bots, mientras que @luna_mx, @diego_campus, @vale_ia, @omar_verifica y @rectoria_iti salen como humanas. Esto coincide con todo lo que ya habíamos encontrado en las Misiones 2 y 3, así que le da más confianza al resultado.

La intervención que priorizaría es reforzar y acelerar el desmentido, en vez de solo enfocarse en mutear a los bots. Esto lo justifico con dos análisis: el árbol de decisión (Misión 5) muestra que la variable más importante para decidir si una cuenta contrarresta en vez de amplificar es si ya existe un desmentido activo, siendo la raíz del árbol, por encima de si la cuenta es bot o tiene muchos seguidores. Y la regresión lineal (Misión 6) lo confirma con números: el coeficiente de bots_activos es positivo (+14.36, amplifica el alcance), mientras que el de desmentidos_activos es negativo (-17.37, reduce el alcance), y el escenario con más desmentidos y sin bots (escenario C) predice el menor alcance de los tres (94.5 cuentas), contra 272.8 si solo hay bots y no hay desmentido.

Una limitación importante de mi análisis es que el dataset es muy pequeño: solo se analizaron 14 tweets en total (Misión 2) y 8 cuentas relacionadas directamente con el rumor del examen (Misión 3), lo cual es una muestra chica comparada con lo que sería un incidente real en redes sociales, donde podrían participar cientos o miles de cuentas. Las conclusiones que saqué son coherentes entre las distintas misiones, pero no necesariamente se podrían generalizar a otro caso de dispersión de rumores sin volver a hacer este mismo tipo de análisis con datos más grandes.

---

## Autochequeo
- [x] Separé origen ≠ bot ≠ amplificador ≠ desmentido
- [x] Usé coseno y timeline (no solo uno)
- [x] Escalé en k-NN y reporté k
- [x] La recomendación sale de M5 y/o M6