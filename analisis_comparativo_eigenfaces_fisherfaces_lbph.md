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

## 6\. Código utilizado

Para la comparación modifiqué el flujo de entrenamiento: en lugar de entrenar un solo modelo con todas las imágenes, se separan los archivos en entrenamiento y prueba según el sufijo del nombre, se entrenan los tres modelos con el mismo conjunto y se evalúan contra las mismas imágenes de prueba, contando aciertos y midiendo el tiempo de cada uno.

```python
import cv2 as cv
import numpy as np
import os
import time

data\_set = "img\\\\caras"
TAMANO = (100, 100)

SUFIJOS\_TRAIN = \["\_orig.jpg", "\_rot15.jpg", "\_rotneg15.jpg", "\_trasladada.jpg", "\_escalada.jpg"]
SUFIJOS\_TEST = \["\_brillomas.jpg", "\_brillomenos.jpg"]


def separar\_train\_test(data\_set):
    personas = sorted(
        d for d in os.listdir(data\_set)
        if os.path.isdir(os.path.join(data\_set, d))
    )

    train\_paths = \[]
    train\_labels = \[]
    test\_paths = \[]
    test\_labels = \[]
    label = 0

    for persona in personas:
        persona\_path = os.path.join(data\_set, persona)
        archivos = os.listdir(persona\_path)

        for archivo in archivos:
            ruta = os.path.join(persona\_path, archivo)

            if any(archivo.endswith(suf) for suf in SUFIJOS\_TRAIN):
                train\_paths.append(ruta)
                train\_labels.append(label)
            elif any(archivo.endswith(suf) for suf in SUFIJOS\_TEST):
                test\_paths.append(ruta)
                test\_labels.append(label)

        print(f"{persona} (label={label}): train={train\_labels.count(label)}, test={test\_labels.count(label)}")
        label += 1

    return train\_paths, train\_labels, test\_paths, test\_labels, personas


def cargar\_imagenes(paths):
    imagenes = \[]
    for p in paths:
        img = cv.imread(p, 0)
        if img is None:
            continue
        img = cv.resize(img, TAMANO)
        imagenes.append(img)
    return imagenes


def entrenar\_y\_evaluar(nombre\_modelo, crear\_modelo, train\_data, train\_labels, test\_data, test\_labels):
    print(f"\\n--- {nombre\_modelo} ---")

    inicio = time.time()
    modelo = crear\_modelo()
    modelo.train(train\_data, np.array(train\_labels))
    tiempo\_entrenamiento = time.time() - inicio
    print(f"Entrenado en {tiempo\_entrenamiento:.1f} segundos")

    aciertos = 0
    confianzas\_correctas = \[]
    confianzas\_incorrectas = \[]

    for img, label\_real in zip(test\_data, test\_labels):
        label\_predicho, confianza = modelo.predict(img)

        if label\_predicho == label\_real:
            aciertos += 1
            confianzas\_correctas.append(confianza)
        else:
            confianzas\_incorrectas.append(confianza)

    total = len(test\_data)
    porcentaje\_acierto = (aciertos / total) \* 100 if total > 0 else 0

    print(f"Aciertos: {aciertos}/{total} ({porcentaje\_acierto:.1f}%)")

    if confianzas\_correctas:
        print(f"Confianza promedio cuando acertó: {np.mean(confianzas\_correctas):.1f}")
    if confianzas\_incorrectas:
        print(f"Confianza promedio cuando falló: {np.mean(confianzas\_incorrectas):.1f}")

    return {
        "modelo": nombre\_modelo,
        "porcentaje\_acierto": porcentaje\_acierto,
        "tiempo\_entrenamiento": tiempo\_entrenamiento,
    }


if \_\_name\_\_ == "\_\_main\_\_":
    train\_paths, train\_labels, test\_paths, test\_labels, personas = separar\_train\_test(data\_set)

    REDUCIR\_TRAIN = 6
    if REDUCIR\_TRAIN > 1:
        train\_paths = train\_paths\[::REDUCIR\_TRAIN]
        train\_labels = train\_labels\[::REDUCIR\_TRAIN]

    train\_data = cargar\_imagenes(train\_paths)
    test\_data = cargar\_imagenes(test\_paths)

    resultados = \[]

    resultados.append(entrenar\_y\_evaluar(
        "Eigenfaces",
        lambda: cv.face.EigenFaceRecognizer\_create(num\_components=50),
        train\_data, train\_labels, test\_data, test\_labels
    ))

    resultados.append(entrenar\_y\_evaluar(
        "Fisherfaces",
        cv.face.FisherFaceRecognizer\_create,
        train\_data, train\_labels, test\_data, test\_labels
    ))

    resultados.append(entrenar\_y\_evaluar(
        "LBPH",
        cv.face.LBPHFaceRecognizer\_create,
        train\_data, train\_labels, test\_data, test\_labels
    ))

    print("\\n\\n========== RESUMEN COMPARATIVO ==========")
    print(f"{'Modelo':<15} {'% Acierto':<12} {'Tiempo (s)':<12}")
    for r in resultados:
        print(f"{r\['modelo']:<15} {r\['porcentaje\_acierto']:<12.1f} {r\['tiempo\_entrenamiento']:<12.1f}")
```

Notas sobre el código:

* El train se reduce tomando 1 de cada 6 imágenes (`REDUCIR\_TRAIN = 6`) y el tamaño se bajó a 100x100 porque Eigenfaces tardaba demasiado con el dataset completo en 150x150. El conjunto de prueba se dejó completo para que el porcentaje de acierto fuera representativo.
* A Eigenfaces se le limitó a 50 componentes (`num\_components=50`) para acelerar el cálculo, ya que sin ese límite calcula todos los componentes posibles y el entrenamiento se alarga mucho.

## 7\. Conclusión

Mi experimento, aunque limitado porque el cambio de brillo fue generado por código y no con luz real, va en la misma dirección que lo que ya se sabe de estos modelos: LBPH fue el más eficiente por mucho en tiempo y sin perder exactitud, Eigenfaces fue el único con fallos (siendo el más sensible a iluminación de los tres), y Fisherfaces quedó en medio, con buena exactitud pero el entrenamiento más lento. Si tuviera que elegir uno para un sistema real con cambios de luz, elegiría LBPH por su velocidad y resistencia a la iluminación. Como siguiente paso, la prueba se podría repetir con fotos tomadas con iluminación real distinta para confirmar estos resultados en condiciones más exigentes.

