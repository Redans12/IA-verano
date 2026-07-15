# Comparativa Eigenfaces, Fisherfaces y LBPH

**Analista:** \[Andres Daniel Ibarrola Origel / 22121298]

## 1\. Qué se hizo

Para esta comparativa utilicé el dataset que ya tenía de capturas de rostros con Haar Cascade, el cual genera 7 variaciones por cada captura: la original, rotación de +15° y -15°, traslación, escalamiento y dos cambios de brillo (uno con más brillo y otro con menos). El dataset tiene dos personas, con aproximadamente la misma cantidad de imágenes cada una.

Para probar qué tan buenos son los modelos con los cambios de luz, dividí las imágenes de la siguiente manera:

* **Entrenamiento:** todas las variaciones que no tienen cambio de brillo (original, rotaciones, traslación y escalamiento)
* **Prueba:** únicamente las imágenes con el brillo modificado (brillomas y brillomenos)

De esta forma los modelos nunca ven imágenes con brillo alterado durante el entrenamiento, y al probarlos con esas imágenes podemos ver qué tanto les afecta el cambio de iluminación.

## 2\. Resultados

|Modelo|% Acierto|Tiempo de entrenamiento|Confianza promedio (aciertos)|
|-|-|-|-|
|Eigenfaces|99.9%|49.1 s|3350.1|
|Fisherfaces|100.0%|76.1 s|16.7|
|LBPH|100.0%|1.2 s|38.7|

Un punto importante es que la confianza no se puede comparar directamente entre los modelos, ya que cada uno la calcula de manera diferente. Que LBPH tenga 38.7 y Eigenfaces 3350.1 no significa que uno sea mejor que el otro, son escalas distintas (por eso cada modelo tiene su propio umbral, como se ve en los ejemplos: <2800 para Eigenfaces, <500 para Fisherfaces y <70 para LBPH).

## 3\. Limitación de la prueba

Los tres modelos salieron con resultados casi perfectos (99.9% y 100%), pero antes de concluir que son perfectos contra la luz hay que aclarar algo.

Las imágenes con brillo alterado no son fotos nuevas tomadas con otra iluminación real, son las mismas capturas del entrenamiento pero con el brillo modificado por código. Es decir, es la misma cara, en la misma posición y en el mismo momento, solo que con los píxeles más claros o más oscuros de manera uniforme. Eso hace que la prueba sea más fácil de lo que sería en la vida real, donde la luz genera sombras, reflejos y cambios que no son uniformes en toda la cara.

Por esto, los resultados demuestran que los tres modelos aguantan bien un cambio de brillo simple y uniforme, pero no demuestran que aguanten igual de bien condiciones de luz reales (como luz de día contra luz de noche, o una lámpara de lado). Para probar eso se necesitarían fotos tomadas en momentos y lugares con iluminación realmente diferente, lo cual no fue posible en esta ocasión.

## 4\. Lo que sí podemos concluir con los datos

* **LBPH fue muchísimo más rápido que los otros dos** (1.2 segundos contra 49 y 76 segundos) sin perder exactitud. Esto se debe a que no hace cálculos pesados sobre toda la imagen como los otros dos, sino que solo compara patrones locales por celdas.
* **Eigenfaces fue el único que tuvo fallos** (3 de 2856 imágenes). Aunque es una diferencia mínima, coincide con que este modelo mira la cara completa como un solo conjunto de píxeles, entonces cualquier cambio de brillo afecta todo ese conjunto al mismo tiempo.
* **Fisherfaces fue el que más tardó en entrenar**, porque además del cálculo que hace Eigenfaces (PCA), hace un cálculo adicional (LDA) para separar mejor a las personas.

## 5\. Lo que ya se sabe de estos modelos (fuera de esta investigación)

Independientemente de mis resultados, estos tres modelos ya tienen diferencias conocidas y documentadas respecto a la iluminación:

* **Eigenfaces** es conocido por ser el más sensible a los cambios de luz de los tres. Esto pasa porque el modelo busca las direcciones donde más varían las imágenes, y los cambios de iluminación generan mucha variación por sí solos, así que el modelo puede confundir la variación de luz con la variación entre personas.
* **Fisherfaces** se creó precisamente como mejora para ese problema. En lugar de solo buscar dónde varían más las imágenes, busca lo que mejor separa a una persona de otra, por lo que resiste mejor los cambios de iluminación y de expresión. Eso sí, necesita varias imágenes por persona para funcionar bien; con pocas muestras se comporta casi igual que Eigenfaces.
* **LBPH** es el que mejor aguanta la iluminación en la práctica, porque no compara el brillo de los píxeles directamente, sino que compara cada píxel contra sus vecinos (si es más claro o más oscuro que ellos). Si toda la imagen se aclara u oscurece de manera pareja, esas comparaciones locales casi no cambian. Por eso es el más usado para tiempo real y para equipos con pocos recursos.

## 6\. Conclusión

Mi experimento, aunque limitado porque el cambio de brillo fue generado por código y no con luz real, va en la misma dirección que lo que ya se sabe de estos modelos: LBPH fue el más eficiente por mucho en tiempo y sin perder exactitud, Eigenfaces fue el único con fallos (siendo el más sensible a iluminación de los tres), y Fisherfaces quedó en medio, con buena exactitud pero el entrenamiento más lento. Si tuviera que elegir uno para un sistema real con cambios de luz, elegiría LBPH por su velocidad y resistencia a la iluminación. Como siguiente paso, la prueba se podría repetir con fotos tomadas con iluminación real distinta para confirmar estos resultados en condiciones más exigentes.

