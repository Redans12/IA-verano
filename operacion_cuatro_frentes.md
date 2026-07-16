# Reporte EDA — Operación Cuatro Frentes
**Analista:** [Andrés Daniel Ibarrola Origel / 22121298]

## Misión 1 — Semáforo Académico
- Pregunta de negocio:¿Qué nivel de riesgo de reprobar tiene cada alumno al cierre del parcial (verde, amarillo o rojo)?
- **Tipo propuesto:** [`clasificar` / predecir] — justificación: Porque lo único que queremos es que cada alumno entre en una categoría, y al ser 3 esto lo convierte en multiclase
- Y / forma de Y: Riesgo
- X (mínimo 5):
    1. asistencia_pct: En la muestra proporcionada se puede observar que los alumnos que menos asisten, son los que se encuentran en color rojo, por lo cual concluí que sí es una métrica que afecta al riesgo
    2. tareas_entregadas: En la muestra se puede observar que aquellos alumnos con la mayor cantidad de tareas se encuentran en color verde, mientras que a medida que disminuye se encuentran en color amarillo y posteriormente en color rojo, lo cual es un indicador directo del riesgo a reprobar
    3. promedio_parciales: El promedio al final nos indica que tan buenas calificaciones tiene el alumno, por lo que aquellos con menor promedio son los más propensos a tener un riesgo en rojo
    4. reprobadas_previas: En la muestra podemos observar que los alumnos con menor cantidad o nulas materias reprobadas se encuentran en color verde, mientras que los que tienen más son propensos a tener un color rojo en su semáforo, lo que nos indica que es una métrica relacionada directamente con la posibilidad de reprobar
    5. horas_plataforma: Al analizar la muestra pude concluir que los alumnos que tienen menores horas en la plataforma se encuentran en color rojo, mientras que los que están en verde tienen la mayor cantidad de horas 
- Hallazgos EDA:
    * En la asistencia<sub>pct</sub> se observa como mientras menor sea, mayor es el riesgo 91$\rightarrow$76$\rightarrow$52
    * En promedio<sub>parciales</sub> es inversamente proporcional al riesgo, entre más alto el riesgo, es menor el promedio del alumno 8.4$\rightarrow$6.8$\rightarrow$5.0
    * Así mismo se repite con reprobadas<sub>previas</sub> pues los que menos posibilidad de reprobar, tienen menor cantidad de materias reprobadas 0.2$\rightarrow$0.9$\rightarrow$2.4
- Distribución de Y: La tabla nos indica que el rojo tiene la menor cantidad de alumnos, mientras que el amarillo solo está un poco por detrás del verde en cuanto a cantidad de alumnos. Este desbalance es moderado, no tan severo como el que vimos en el ejercicio del dino, pero de igual forma justifica no depender solo de accuracy como métrica principal, como ya se explica en la sección de métricas.
- Calidad de datos: Un problema que podría suceder sería inconsistencia en los datos, por ejemplo que se presente asistencia_pct = 0 pero tareas_entregadas = 9 porque no es posible que un alumno entregue tareas si no asiste a clases, y entonces nos daría un problema al momento de buscar clasificar o usar la variable asistencia_pct para la clasificación
- Leakage evitado: No la usaría porque lo que buscamos es clasificar un riesgo de algo que no ha sucedido, si usaramos dicha x, todo el propósito de la clasificación no tendría sentido pues solo tendríamos que ponerlos en aprobado o reprobado
- Métricas coherentes con mi tipo: Como es un problema de clasificación multiclase, no usaría solo accuracy, aunque el desbalance de las clases (40%/35%/25%) no es tan grave como el que vimos en el ejercicio del dino. El motivo es que no todos los errores son igual de graves: si el modelo confunde a un alumno rojo (riesgo alto) con verde, es mucho peor que si confunde un verde con amarillo, porque ese alumno en riesgo real no sería detectado a tiempo. Por eso usaría recall enfocado en la clase rojo, para saber qué tan bien detecta el modelo a los alumnos que realmente están en riesgo alto, y F1 por clase para tener un balance entre precision y recall en las tres categorías. Sí reportaría accuracy también, pero solo como referencia general, no como la métrica principal para decidir si el modelo es bueno.
- Modelo propuesto y condición: En base a todo el análisis, yo optaría por usar un árbol de decisión. Esto debido a que los árboles manejan muy bien la multiclase, no necesitamos escalar variables, y justamente como mencioné anteriormente, si tenemos algo como asistencia_pct<60 es directamente la forma en que se hacen o clasifican los nodos en los árboles

## Misión 2 — Alerta de Churn
- Pregunta de negocio: ¿Este alumno abandonará la materia?
- **Tipo propuesto:** [`clasificar` / predecir] — justificación: Lo que buscamos es poner al alumno en alguna de las dos opciones que tenemos, lo cual quiere decir que lo clasificamos. Es de clase binaria pues solo tenemos dos opciones 0=permanece 1=abandona
- Distribución de Y e implicaciones: Abandona, tal como podemos ver en la tabla y en la pregunta de negocio, lo que buscamos conocer es si al final el alumno permanece o abandona la clase, asignándole un valor a abandona podemos conocer que es lo que pasará 
- Tratamiento de NA: Con N = 500 y 14% de abandona=1: 500 × 0.14 = 70 alumnos que sí abandonan (y 430 que no).
Si alguien reportara "86% de aciertos" sin más contexto, ese número por sí solo no dice nada útil. Un modelo que no aprendiera absolutamente nada y simplemente predijera "no abandona" para todos los alumnos, sin revisar ningún dato, acertaría automáticamente en el 86% de los casos (los 430 que en efecto no abandonan), sin haber detectado ni un solo caso real de abandono. Por eso el 86% de accuracy no demuestra que el modelo sea bueno; solo refleja el desbalance natural de las clases. Aquí, igual que en el caso de died en el ejercicio del dino, hace falta una métrica que sí mida si el modelo detecta los casos de abandono (como recall o F1), no solo qué tan seguido acierta en general.
- Métricas y costo de error: 
- Modelo propuesto:

## Misión 3 — Pronóstico de Puntaje
- Pregunta de negocio:
- **Tipo propuesto:** [clasificar / predecir] — justificación:
- Qué se gana/pierde si se convierte a aprobado/reprobado:
- Outliers / errores de captura:
- Métricas (2):
- Modelo propuesto:

## Misión 4 — Tiempo de Estudio
- Pregunta de negocio:
- **Tipo propuesto:** [clasificar / predecir] — justificación:
- Hipótesis dificultad → horas:
- Cola larga: ¿borrar o conservar?
- Alternativa de binarizar Y:
- Métricas y modelo + 2 chequeos EDA:

## Síntesis (máx. 8 líneas)
1. Tabla resumen de *mis* cuatro propuestas de tipo (M1–M4).
2. Una pista que usé para decidir “clase vs número” en cualquier misión.
3. Frase final: “El tipo de problema se deduce de la pregunta y de Y porque…”