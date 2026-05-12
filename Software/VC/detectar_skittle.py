from picamera2 import Picamera2
import cv2
import numpy as np
import time

# -----------------------------
# 1. Configurar cámara
# -----------------------------

picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)

picam2.configure(config)
picam2.start()

# Dejamos que la cámara se estabilice
time.sleep(2)


# -----------------------------
# 2. Función para detectar color
# -----------------------------

def detectar_color(hsv_roi):
    """
    Recibe una imagen en HSV de la zona donde está el Skittle
    y devuelve el color detectado.
    """

    rangos_colores = {
        "rojo": [
            # El rojo en HSV está partido en dos zonas
            (np.array([0, 80, 80]), np.array([10, 255, 255])),
            (np.array([170, 80, 80]), np.array([180, 255, 255]))
        ],

        "verde": [
            (np.array([35, 60, 60]), np.array([85, 255, 255]))
        ],

        "azul": [
            (np.array([90, 80, 80]), np.array([130, 255, 255]))
        ],

        "amarillo": [
            (np.array([20, 80, 80]), np.array([35, 255, 255]))
        ],

        "naranja": [
            (np.array([10, 80, 80]), np.array([20, 255, 255]))
        ],

        "morado": [
            (np.array([130, 50, 50]), np.array([165, 255, 255]))
        ]
    }

    puntuaciones = {}

    for nombre_color, rangos in rangos_colores.items():
        mascara_total = None

        for limite_inferior, limite_superior in rangos:
            mascara = cv2.inRange(hsv_roi, limite_inferior, limite_superior)

            if mascara_total is None:
                mascara_total = mascara
            else:
                mascara_total = cv2.bitwise_or(mascara_total, mascara)

        # Cuenta cuántos píxeles de la zona pertenecen a ese color
        puntuaciones[nombre_color] = cv2.countNonZero(mascara_total)

    # Nos quedamos con el color que más píxeles tiene
    color_detectado = max(puntuaciones, key=puntuaciones.get)
    mejor_puntuacion = puntuaciones[color_detectado]

    # Si hay muy pocos píxeles de color, asumimos que no hay Skittle
    if mejor_puntuacion < 300:
        return "ninguno", puntuaciones

    return color_detectado, puntuaciones


# -----------------------------
# 3. Bucle principal
# -----------------------------

while True:
    # Capturamos imagen de la cámara
    frame_rgb = picam2.capture_array()

    # OpenCV trabaja normalmente en BGR, así que convertimos
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    # Tamaño de la imagen
    alto, ancho, _ = frame_bgr.shape

    # -----------------------------
    # 4. Definir zona central de análisis
    # -----------------------------
    # Aquí asumimos que colocarás el Skittle en el centro de la imagen.

    x1 = ancho // 2 - 100
    x2 = ancho // 2 + 100
    y1 = alto // 2 - 100
    y2 = alto // 2 + 100

    roi = frame_bgr[y1:y2, x1:x2]

    # Convertimos esa zona a HSV
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Detectamos color
    color, puntuaciones = detectar_color(hsv_roi)

    # -----------------------------
    # 5. Mostrar resultado
    # -----------------------------

    if color == "ninguno":
        texto = "No detecto ningun Skittle"
    else:
        texto = f"Es de color {color}"

    # Dibujamos el cuadrado donde hay que poner el Skittle
    cv2.rectangle(
        frame_bgr,
        (x1, y1),
        (x2, y2),
        (255, 255, 255),
        2
    )

    # Escribimos el resultado en la imagen
    cv2.putText(
        frame_bgr,
        texto,
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )

    # También lo imprimimos por terminal
    print(texto, puntuaciones)

    # Mostramos la imagen
    cv2.imshow("Detector de Skittles", frame_bgr)

    # Si pulsas q, se cierra
    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord("q"):
        break


# -----------------------------
# 6. Cerrar todo correctamente
# -----------------------------

picam2.stop()
cv2.destroyAllWindows()
