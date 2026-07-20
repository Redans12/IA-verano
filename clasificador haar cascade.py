import numpy as np
import cv2 as cv

rostro = cv.CascadeClassifier('haarcascade_frontalface_alt2.xml')

# ---------- Cambio principal: video en vez de cámara ----------
VIDEO_PATH = 'video_cillian.mp4'  # <-- pon aquí el nombre/ruta de tu video
cap = cv.VideoCapture(VIDEO_PATH)

x = y = w = h = 0
img = None
count = 0

VARIACIONES_POR_CAPTURA = 7  # orig, rot15, rotneg15, trasladada, escalada, brillomas, brillomenos
MAX_ARCHIVOS = 5000
MAX_DETECCIONES = MAX_ARCHIVOS // VARIACIONES_POR_CAPTURA  # 714


# ---------- Funciones de transformación (data augmentation) ----------

def rotar(imagen, angulo):
    (h, w) = imagen.shape[:2]
    centro = (w // 2, h // 2)
    M = cv.getRotationMatrix2D(centro, angulo, 1.0)
    return cv.warpAffine(imagen, M, (w, h))


def trasladar(imagen, tx, ty):
    (h, w) = imagen.shape[:2]
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv.warpAffine(imagen, M, (w, h))


def escalar(imagen, factor):
    return cv.resize(imagen, None, fx=factor, fy=factor, interpolation=cv.INTER_LINEAR)


def cambiar_brillo(imagen, valor):
    return cv.convertScaleAbs(imagen, alpha=1.0, beta=valor)


def guardar_variaciones(imagen, count):
    base_name = f'img/caras/cillian/cillian{count}'  # <-- carpeta y nombre de la persona

    cv.imwrite(f'{base_name}_orig.jpg', imagen)
    cv.imwrite(f'{base_name}_rot15.jpg', rotar(imagen, 15))
    cv.imwrite(f'{base_name}_rotneg15.jpg', rotar(imagen, -15))
    cv.imwrite(f'{base_name}_trasladada.jpg', trasladar(imagen, 10, 10))
    cv.imwrite(f'{base_name}_escalada.jpg', escalar(imagen, 1.2))
    cv.imwrite(f'{base_name}_brillomas.jpg', cambiar_brillo(imagen, 40))
    cv.imwrite(f'{base_name}_brillomenos.jpg', cambiar_brillo(imagen, -40))


# ---------- Loop principal ----------

while True:
    ret, frame = cap.read()

    # ---------- Cambio importante: si el video se acabó, ret sale False ----------
    # Con webcam esto casi nunca pasa, pero con video hay que cortar el loop
    # o si no, cv.cvtColor truena porque frame ya es None.
    if not ret:
        print("Video terminado.")
        break

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    rostros = rostro.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in rostros:
        if count >= MAX_DETECCIONES:
            break

        img = frame[y:y + h, x:x + w]
        #frame = cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        count += 1
        guardar_variaciones(img, count)

    cv.imshow('rostros', frame)

    if img is not None:
        cv.imshow('cara', img)

    k = cv.waitKey(1)
    if k == 27 or count >= MAX_DETECCIONES:
        break

cap.release()
cv.destroyAllWindows()

print(f"Total de detecciones guardadas: {count}")
print(f"Total de archivos generados: {count * VARIACIONES_POR_CAPTURA}")