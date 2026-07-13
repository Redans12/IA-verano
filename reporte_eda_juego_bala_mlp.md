# Reporte EDA — Juego Bala + Salto + MLP

**Analista:** \[Andrés Daniel Ibarrola Origel / 22121298]

## 1\. Problema y dataset

### ¿Saltará el jugador en este frame?

* **Y:** Columna binaria llamada `salto`, donde 1 = el jugador está en el aire (saltando) y 0 = el jugador está en el suelo. El objetivo es que el modelo aprenda a imitar el estilo de salto del jugador.
* **X (variables de entrada):**

  * `velocidad\_bala`: velocidad a la que se mueve la bala hacia el jugador (es negativa porque va de derecha a izquierda). Es importante porque a mayor velocidad, el jugador tiene que saltar cuando la bala está más lejos.
  * `distancia`: distancia en píxeles entre el jugador y la bala. Es la variable más importante porque el salto depende directamente de qué tan cerca está la bala.
* **Granularidad:** una fila por cada frame mientras la bala está disparada. El juego registra la decisión (saltar o no) en cada frame del modo manual, no un resumen por partida.
* **Tamaño mínimo de dataset:** el propio código exige un mínimo de 80 muestras para entrenar. Sin embargo, para que el modelo generalice bien conviene jugar varias rondas con balas de diferentes velocidades (el rango va de -12 a -6), para que el dataset cubra casos de balas rápidas y lentas.
* **Riesgo si el dataset está mal definido:** si el jugador solo juega unas pocas rondas o siempre con el mismo estilo, el modelo solo aprenderá ese caso específico. Por ejemplo, si todas las balas registradas fueron lentas, el modelo no sabrá reaccionar a tiempo con una bala rápida porque nunca vio esa situación.

## 2\. Diccionario de datos

|Columna|Tipo|Descripción|
|-|-|-|
|velocidad\_bala|numérica (float)|Velocidad de la bala en píxeles por frame, negativa porque avanza hacia la izquierda|
|distancia|numérica (float)|Distancia absoluta entre el jugador y la bala en píxeles|
|salto|binaria 0/1|1 durante todo el tiempo que el jugador está en el aire, 0 cuando está en el suelo|

**Observaciones del diccionario:**

* La etiqueta `salto` no marca solo el frame exacto donde se presionó la tecla, sino todos los frames en que el jugador está en el aire. Esto hace que la clase 1 tenga más ejemplos que si solo se marcara el frame del brinco.
* Solo se registran filas cuando la bala está disparada (`bala\_disparada = True`), lo cual está bien porque cuando no hay bala no hay decisión que tomar.
* Una posible columna faltante sería la posición vertical del jugador, aunque para este problema tan simple con `distancia` y `velocidad\_bala` es suficiente.

## 3\. Checklist EDA

**¿La clase objetivo está balanceada?**
No completamente, pero el desbalance no es tan grave. Como `salto=1` se marca durante todo el tiempo en el aire (varios frames por cada brinco) y no solo en un frame, la clase positiva tiene una cantidad razonable de ejemplos. Aun así, el jugador pasa más tiempo en el suelo que en el aire, así que se espera que haya más filas con salto=0. El código usa `stratify=y` en el train\_test\_split, lo cual ayuda a mantener la proporción de clases en entrenamiento y prueba.

**¿Hay fugas de información (leakage)?**
No se detecta leakage en las variables usadas. Tanto `velocidad\_bala` como `distancia` son datos disponibles en el momento de la decisión, no información del futuro. La etiqueta se registra en el mismo frame en que ocurre el estado (aire o suelo), así que el modelo aprende a asociar la situación actual con la acción actual, que es lo que se busca al imitar al jugador.

**¿Datos i.i.d.?**
No, los frames consecutivos no son independientes: si en un frame la distancia es 200, en el siguiente será casi la misma menos la velocidad. Además todos los frames de un mismo salto tienen etiqueta 1 seguida. El código divide train/test con un split aleatorio por fila, lo que puede inflar un poco la accuracy reportada porque frames casi idénticos pueden caer uno en entrenamiento y otro en prueba. Para un ejercicio simple es aceptable, pero es un punto a tener en cuenta al interpretar el accuracy.

**¿Outliers?**
Podrían aparecer distancias muy grandes al inicio (cuando la bala apenas sale) o casos raros si el jugador salta cuando la bala está lejísimos sin necesidad. Estos no son errores de captura sino decisiones humanas inconsistentes, y de hecho el modelo las va a imitar. Si el jugador jugó mal, el modelo aprenderá a jugar mal.

## 4\. Interpretación

* El dataset tiene solo 2 variables de entrada, lo cual hace que el problema sea de baja dimensión y se pueda visualizar completo en una gráfica 2D (el código ya incluye esta gráfica: distancia vs velocidad, coloreando por salto).
* Se espera ver en la gráfica una zona clara: puntos rojos (salto=1) concentrados en distancias cortas, y azules (salto=0) en distancias grandes. La frontera entre ambos puede cambiar según la velocidad de la bala.
* Si la gráfica muestra las dos clases bien separadas, el problema es sencillo y casi cualquier clasificador funcionará.
* El escalado con StandardScaler que aplica el código es correcto, porque las dos variables tienen rangos muy diferentes (velocidad entre -12 y -6, distancia de 0 a cientos de píxeles).

## 5\. Elección de modelo

|Hallazgo del EDA|Tipo de problema|Modelo|
|-|-|-|
|Y binaria, solo 2 variables numéricas, relación probablemente simple (distancia corta = saltar)|Clasificación binaria|Red neuronal pequeña MLP de 2 capas ocultas con 3 neuronas cada una, como la que ya implementa el código|

**Justificación:** el problema es tan simple que hasta una regresión logística o una regla fija (si distancia < umbral entonces saltar) podrían funcionar. Se usa un MLP pequeño (3,3) porque el objetivo del ejercicio es practicar redes neuronales, y su tamaño reducido es adecuado: con solo 2 variables y un dataset chico, una red más grande solo memorizaría los datos (sobreajuste) sin aprender el patrón general.

**Condiciones que deben cumplirse:**

1. Tener ejemplos de ambas clases (el código ya contempla el caso de una sola clase con el "modelo trivial").
2. Que el dataset cubra diferentes velocidades de bala, no solo una.

## Síntesis

El dataset se genera jugando en modo manual, donde cada frame con bala activa produce una fila con velocidad, distancia y si el jugador estaba en el aire. El EDA muestra un problema de clasificación binaria simple, con solo dos variables de entrada, clases razonablemente representadas y sin leakage. Los frames no son independientes entre sí, lo que puede inflar un poco la accuracy del split aleatorio. Con dos variables y una relación tan directa (a menor distancia, saltar), un MLP pequeño de (3,3) neuronas es más que suficiente; un modelo más complejo no se justifica con este volumen y simplicidad de datos.

