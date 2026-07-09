# Reporte EDA — Operación Dino Crash

**Analista:** \[Andrés Daniel Ibarrola Origel / 22121298]

## 1\. Problema y dataset (Misión 1)

### P1 — ¿Morirá en el siguiente frame?

* **Y:** Columna de tipo binaria la cual representa 0=morirá 1=vivirá
* **X (mínimo 5 variables):**

  * Distancia: Determinamos a cuántos frames de distancia se encuentra el siguiente obstáculo
  * Velocidad: velocidad a la cual se acercan los obstáculos
  * Altura: altura del siguiente obstáculo
  * Tiempo transcurrido: Con este podemos conocer qué tan avanzado se encuentra en el juego e intentar intuir la dificultad de los próximos obstáculos
  * Salto: verificar si el dinosaurio se encuentra en el piso o en el aire (si se ejecuta un salto estando en el aire, esta acción se ignorará)
* **Granularidad:** un frame cada 16ms porque con esto podremos obtener la información requerida para las variables x, y
* **Tamaño mínimo de dataset:** 300 partidas mínimas (cada una con sus frames correspondientes) lo que nos proporciona miles de filas para tener suficiente información debido a que existen diferentes variables incluso en cada partida, como lo son: el tiempo de aparición del primer obstáculo, distancia entre obstáculos, altura de los obstáculos y el incremento de velocidad que estos van adquiriendo conforme pasa la partida.
* **Riesgo si el dataset está mal definido:** Si el dataset se encuentra mal definido puede causar que el dinosaurio quede estancado en situaciones específicas las cuales nunca se presentaron en el dataset, así como acciones que no conoce y no le permita continuar de cierto punto (aunque cada partida es aleatoria, sigue ciertos patrones en distintos puntos de esta). Por ejemplo si se omite la variable altura, el dinosaurio podría saltar a una altura no suficiente y jamás avanzar al momento de presentarse un obstáculo más alto

### P2 — ¿Cuántos puntos alcanzará esta partida al morir?

* **Y:** Numérica, la cual indica el puntaje de cada partida
* **X (mínimo 5 variables):**

  * Velocidad a la que murió: Esto nos indica si hay un punto de inflexión y si la pérdida de la partida está ligada directamente con la velocidad a la que aparecían los obstáculos
  * Cantidad de obstáculos: Cuántos obstáculos en pantalla había al momento de morir, esto nos permite saber si al momento de aparecer más obstáculos es más probable que termine la partida
  * Tipo de fallo: Saber si el fallo en las partidas anteriores se dio debido a que no se saltó a tiempo o si no se saltó con la altura suficiente para evitar el obstáculo
  * Obstáculos evitados: cuántos obstáculos se lograron evitar exitosamente antes de perder
  * Tiempo de cada partida: Con esto podemos conocer que tan lejos se llegó y cuál es el tiempo probable para las siguientes partidas (el tiempo vivo está directamente relacionado con el puntaje)
* **Granularidad:** Debido a que buscamos conocer cuántos puntos se alcanzarán en la siguiente partida, aquí necesitamos un resumen por partida para poder obtener todas las variables necesarias
* **Tamaño mínimo de dataset:** Con un mínimo de 100 partidas podemos obtener toda la información necesaria ya que al no tener que tomar decisiones, solo predecir algo, podemos usar la probabilidad con los datos presentados para tener una buena exactitud
* **Riesgo si el dataset está mal definido:** Si se omite algún dato o variable se corre el riesgo que no se tome en cuenta y el pronóstico de puntaje sea completamente erróneo. Por ejemplo si omitimos la cantidad de obstáculos al momento de perder, sería imposible predecir que pasará en un escenario donde esto suceda (lo cual está ligado al avance del juego, ya que, mientras más se avance, más obstáculos juntos aparecen)

### P3 — ¿Qué tipo de obstáculo viene próximo?

* **Y:** Binaria para poder saber si es un frame=0 o un evento=1
* **X (mínimo 5 variables):**

  * Color: El color del siguiente frame que aparezca, esto nos va ayudar a identificar qué tipo de obstáculo viene o si no viene ninguno
  * Altura: La altura del siguiente obstáculo nos permitirá saber su tipo, si es un cactus pequeño o grande, o si se trata de algo más, si no hay una altura podemos determinar que no hay obstáculo
  * Ancho: Al igual que la altura, cada obstáculo tiene un ancho diferente y nos permitirá clasificarlo o determinar si no hay obstáculo
  * Velocidad: mientras más se avanza en el juego, el tipo de obstáculo cambia, sabiendo la velocidad podemos determinar cuánto avance tiene la partida y cuáles obstáculos se presentarán, así como si es probable que no haya ninguno
  * Frame: Con este determinamos la diferencia o estado en el que se encuentra nuestro juego, sabemos que es lo que ocurre y la información puede ser utilizada para tomar decisiones e intuir el siguiente
* **Granularidad:** En este caso se necesita un frame cada 16ms pues lo que queremos determinar es el siguiente obstáculo y con esta información nos permite conocerlo
* **Tamaño mínimo de dataset:** Al menos 100 frames distintos, esto nos permitirá cubrir todos los distintos tipos de obstáculos y escenarios para poder hacer la distinción
* **Riesgo si el dataset está mal definido:** Si ocurre un error, como en la clasificación de los frames, es probable que se piense que cuando no hay nada, en realidad exista un obstáculo y falle, o viceversa y salte en un momento no adecuado

## 2\. Diccionario y muestra (Misión 2)

* **Patrón en died=1:** En los frames anteriores el dinosaurio salta cuando los obstáculos se encuentran a una distancia razonable, pero en el frame 82 la variable jump=0 lo que significa que no saltó a tiempo o justamente acababa de aterrizar
* **¿score es buena variable para predecir muerte en el siguiente frame? ¿Por qué sí o no?** No. ya que score lo único que nos indica es el tiempo o distancia que se ha recorrido, no tiene ninguna relación con los obstáculos
* **¿Falta alguna columna crítica para P1?** Sí, la altura del dinosaurio para saber si se tiene que agachar cuando aparece un pterodáctilo, también una columna que nos indique si el dinosaurio está agachado, ya que si sí lo está, este no puede saltar
* **¿died tal como está definida sirve para P1 o solo describe el final de la partida?** No, ya que este solo nos indica si el dinosaurio está vivo o no, no ayuda en nada a predecir el siguiente frame, para esto podríamos agregar una columna llamada died\_next en donde se indique si se muere en el siguiente frame, por ejemplo en el frame 81, esta variable sería died\_next=1

## 3\. Checklist EDA (Misión 3)

|Pregunta EDA|¿Qué buscas?|Si la respuesta es mala, ¿qué modelo evitas o qué haces?|
|-|-|-|
|3. ¿La clase objetivo está balanceada? No realmente porque en las muestras que nos podemos basar para pensar en un dataset completo, solo 2 de las 10 filas tienen died=1, y en ambas son el último frame de su partida. Si una partida dura en promedio 150-200 frames y sólo el último tiene died=1, eso significa que menos del 1% de los frames totales corresponden a muerte. Con las 300 partidas propuestas y un promedio de 200 frames, tendríamos solo unos 300 casos de died=1 contra al rededor de 59,700 de died=0. Es un gran desvalance y la consecuencia podría ser que el modelo predijera siempre que "no muere" y aunque podría acertar la mayor parte de las veces, sería inútil porque no podría detectar el caso que realmente importa|% muerte vs no-muerte por frame|Métrica accuracy engañosa; considerar F1, ponderar clases|
|4. ¿Hay fugas de información (leakage)? Si usamos la columna died como variable objetivo para P1 sin modificarla died solo nos marca 1 en el frame exacto en donde la partida termina. Como P1 busca predecir, si usamos died tal cual, el modelo predeciría algo que ya se sabe en ese mismo frame. Aquí tendriamos que desplazar la columna un paso hacia atrás al frame anterior al de muerte|¿Y incluye el futuro?|Cualquier modelo "perfecto" en validación falsa|
|7. ¿Outliers? No se observan outliers evidentes, sin embargo, en el dataset completo podemos esperar revisar cosas como: valores de dist\_obstacle negativos (que no pueden ocurrir), valores de speed fuera de rango razonable, o saltos bruscos en frame dentro de una misma partida, que puede deberse a frames faltantes o corruptos. Si esto llegara a pasar, la acción antes de entrenar sería limpiarlos o eliminarlos, y también decidir si se trata de un bug del juego y podríamos dejarlos para que se tomen en cuenta ya que es algo que puede suceder|dist\_obstacle negativo, saltos imposibles|Limpiar antes de entrenar|

**Para la pregunta 8 (i.i.d.): explica por qué mezclar frames de la misma partida en entrenamiento y prueba es un error.**

Los frames de una misma partida no son independientes entre sí, pues el frame 82 depende directamente de lo que pasó en el frame 81. Si mezclamos frames de la misma sesión entre entrenamiento y prueba, el modelo podría generar en entrenamiento información igual a la que se le pide que prediga en la prueba. Lo que debemos hacer es dividir el entrenamiento y la prueba por sesión completa, no por fila individual para que el modelo se evalúe con partidas que nunca vio antes

**Da un ejemplo concreto de data leakage usando score o time\_ms en P1.**

Para el ejemplo usemos time\_ms total de la duración de la partida (o score final con el que se terminó la partida) como variable de entrada (X) para predecir si el dinosaurio morirá en el siguiente frame, este valor solo se conoce una vez que la partida finaliza, es decir, solo existe cuando ya sabemos que la muerte ocurrió y en qué momento. Si lo usamos como predictor, sería darle al modelo información del futuro para predecir un evento que ocurre antes de que realmente pase. En cambio si usamos time\_ms o score del frame actual, sin saber cuánto durará la partida en total, si funciona porque es información disponible en tiempo real sin adelantarnos a lo que pasará

## 4\. Interpretación de resúmenes (Misión 4)

1. **¿El problema P1 (muerte en siguiente frame) está desbalanceado? Cuantifica con los números dados.** Sí están desvalanceados, la tabla indica que de aproximadamente 12,000 frames totales, solo hay 50 casos con died=1. Sería un 0.4% de los frames, es decir, por cada frame de muerte hay 240 de no muerte. Esto confirma lo que se planteó anteriormente en la misión 3
2. **¿Qué implica eso para la métrica que usarías? (accuracy vs precision/recall/F1).** Para el modelo esto implica que siempre se prediga que no morirá porque tendría 99.6% de acertividad sin haber aprendido algo que realmente sirve. Tenemos que usar métricas que evalúen específicamente qué tan bien se detecta las muertes reales. Priorizar algo como recall (de las muertes reales, cuántas se detectaron) para que tenga sentido el porque el costo de no anticipar una muerte es peor que el costo de una falsa alarma
3. **¿dist\_obstacle parece útil como predictor? Argumenta con la fila de muertes.** Sí, porque con los datos se nos indica que las muertes suelen ocurrir con dist\_obstacle < 20. Esto nos dice que la separación es clara, pues los valores de dist\_obstacle en los frames de muerte están muy por debajo del comportamiento normal, lo cual es justo el tipo de señal que un modelo necesita para distinguir si morirá o no
4. **¿La distribución de score sugiere regresión simple o necesitas transformación / otro enfoque?** Sugiere que no conviene una regresión lineal simple sin ajustes. Podemos observar una cola larga hacia la derecha, esto podríamos verlo como una distribución sesgada, no simétrica y una regresión lineal asume errores más o menos simétricos. Aquí podríamos aplicar una transformación al score antes de modelar o considerar un modelo que no sea sensible a la forma de distribución, como por ejemplo un árbol de regresión

## 5\. Elección de modelo (Misiones 5–6)

|Escenario|Fila de la guía que aplica|Modelo que propondrías|2 condiciones que deben cumplirse|
|-|-|-|-|
|P1|Y binaria muy desbalanceada|Regresión logística con class\_weight balanceado, o árbol de decisión con umbral ajustado|(1) Tener suficientes casos positivos tras el balanceo para que el modelo aprenda el patrón, no solo ruido. (2) Dividir train/test por sesión completa, no por frame suelto (por el punto de i.i.d. que ya vimos)|
|P2|Y numérica (score final)|Regresión lineal simple, o árbol de regresión si la relación no es lineal|(1) Las X usadas no deben tener leakage (nada de time\_ms total ni variables que solo existan al morir). (2) Relación razonablemente estable entre X e Y — si no es lineal, usar el árbol en vez de forzar una recta|
|P3|Y categórica multiclase|Regresión logística multinomial, o árbol de decisión|(1) Cada clase (none, cactus\_small, cactus\_large, bird) debe tener representación suficiente, no solo una o dos dominando. (2) Las X no deben derivarse del obstáculo mismo (nada de altura/ancho/color, por el leakage circular que ya identificamos)|

**Contraejemplos (Misión 6):**

1. **Describe un escenario del dino donde un árbol profundo parecería buena idea pero el EDA lo desaconsejaría.** Para P1, un árbol de decisión profundo podría parecer funcional porque aprendería patrones específicos de cada situación, pero el EDA nos mustró que solo hay al rededor de 300 casos de died=1 en todo el dataset, representando el 0.4%. Con tan pocos ejemplos positivos un árbol profundo terminaría memorizando esos 300 casos particulares en vez de aprender el patrón general (sería sobreajuste)
2. **Describe un escenario donde una red neuronal tendría sentido y qué deberías ver en el EDA para justificarla.** Si en vez de 300 partidas tuviéramos cientos de miles de partidas y quisiéramos obtener patrones de secuencias completas, ahí una red neuronal tendría sentido, porque estas redes están hechas para aprender de secuencias temporales. Para justificarlas en el EDA necesitaríamos un volumen de datos mayor, evidencia de que las variables simples por sí solas no explican el resultado, lo que sugeriría que hay patrones más complejos en la secuencia de frames que un modelo simple no podría capturar
3. **¿Se podría resolver P1 con reglas fijas (si dist\_obstacle < X y jump=0 entonces muerte)? Compara con un modelo aprendido: ventajas y límites.** Sí, con una regla como "si dist\_obstacle < 20 y jump==0, entonces predecir muerte" ya captura buena parte de la señal que vimos en el EDA. La ventaja de la regla simple es que es simple y transparente, y no necesita entrenamiento ni datos de sobra, también es fácil de corregir si falla. En cuanto a limitantes, un solo umbral no captura que el umbral seguro cambia con la velocidad, ni con el tipo de obstáculo. Un modelo aprendido puede combinar distintas variables y ajustar el umbral de forma automática y más precisa.

## Síntesis (5 líneas)

Antes de elegir cualquier modelo, el dataset que pediría primero sería el completo de las 300 partidas propuestas en la misión 1, con las columnas del diccionario más las variables faltantes identificadas (altura del dinosaurio, estado del salto en curso, etc.) Solo después de revisar el EDA, balance de clases, correlaciones, outliers y ausencia de leakage tendría sentido elegir el modelo. Para p1, regresión logística balanceada debido al desbalance de clases. Para p2, regresión lineal o árbol de regresión evitando variables contaminadas. Para p3, árbol, evitando variables que describan directamente el obstáculo, En ningún caso se justifica con los datos que se nos proporcionan, usar modelos complejos como redes neuronales

