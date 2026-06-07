import cv2
import numpy as np
from pathlib import Path

CARPETA = Path(__file__).parent

def trobar_imatges(carpeta):
    """
    Busca imatges evitant duplicats.
    """
    extensions = ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG", "*.png", "*.PNG"]

    imatges = []
    vistos = set()

    for extensio in extensions:
        for ruta in carpeta.glob(extensio):
            clau = str(ruta.resolve()).lower()
            if clau not in vistos:
                vistos.add(clau)
                imatges.append(ruta)

    return sorted(imatges, key=lambda p: p.name.lower())

IMAGENES = trobar_imatges(CARPETA)

# ============================================================
# LECTURA ROBUSTA D'IMATGES
# ============================================================

def leer_imagen(ruta_imagen):
    """
    Llegeix imatges en Windows encara que la ruta tingui accents o caracters especials.
    """
    try:
        datos = np.fromfile(str(ruta_imagen), dtype=np.uint8)
        imagen = cv2.imdecode(datos, cv2.IMREAD_COLOR)
        return imagen
    except Exception as error:
        print(f"Error llegint la imatge {ruta_imagen}: {error}")
        return None

# ============================================================
# CLASSIFICACIO DE COLOR
# ============================================================

def clasificar_color_hsv(h, s, v):
    """
    Classifica color a partir de HSV. OpenCV usa H entre 0 i 179.
    """

    if v < 45:
        return "molt fosc / ombra"

    if s < 45 and v > 150:
        return "blanc / gris clar"

    if (h < 20 or h >= 170) and v < 130 and s < 180:
        return "marro"

    if h < 10 or h >= 170:
        return "vermell"

    if 10 <= h < 24:
        return "taronja"

    if 24 <= h < 40:
        return "groc"

    if 40 <= h < 85:
        return "verd"

    if 85 <= h < 130:
        return "blau"

    if 130 <= h < 160:
        return "lila"

    if 160 <= h < 170:
        return "rosa / vermell clar"

    return "color desconegut"

# ============================================================
# SELECCIO DEL CONTORN DEL SKITTLE
# ============================================================

def seleccionar_contorn_skittle(contornos, shape):
    """
    Selecciona el contorn que mes sembla un skittle:
    - area raonable
    - forma circular
    - no toca les vores
    - no es una regio enorme del fons
    """

    alto, ancho = shape[:2]
    area_imatge = alto * ancho

    millor_contorn = None
    millor_score = -1

    centre_imatge_x = ancho / 2
    centre_imatge_y = alto / 2

    for contorno in contornos:
        area = cv2.contourArea(contorno)

        if area < 150:
            continue

        if area > area_imatge * 0.10:
            continue

        perimetre = cv2.arcLength(contorno, True)

        if perimetre == 0:
            continue

        circularitat = 4 * np.pi * area / (perimetre * perimetre)

        if circularitat < 0.45:
            continue

        x, y, w, h = cv2.boundingRect(contorno)

        marge = 5
        toca_vora = (
            x <= marge or
            y <= marge or
            x + w >= ancho - marge or
            y + h >= alto - marge
        )

        if toca_vora:
            continue

        ratio = w / h if h != 0 else 0

        if ratio < 0.55 or ratio > 1.45:
            continue

        cx = x + w / 2
        cy = y + h / 2

        distancia_centre = np.sqrt(
            (cx - centre_imatge_x) ** 2 + (cy - centre_imatge_y) ** 2
        )

        distancia_normalitzada = distancia_centre / np.sqrt(ancho ** 2 + alto ** 2)

        score = area * circularitat * (1 - distancia_normalitzada)

        if score > millor_score:
            millor_score = score
            millor_contorn = contorno

    return millor_contorn

# ============================================================
# DETECCIO DEL COLOR DEL SKITTLE
# ============================================================

def detectar_color_skittle(ruta_imagen):
    imagen = leer_imagen(ruta_imagen)

    if imagen is None:
        print(f"{ruta_imagen.name} -> No s'ha pogut llegir la imatge")
        return None

    alto_original, ancho_original = imagen.shape[:2]
    max_width = 700

    if ancho_original > max_width:
        escala = max_width / ancho_original
        imagen = cv2.resize(imagen, None, fx=escala, fy=escala)

    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    lower = np.array([0, 70, 45])
    upper = np.array([179, 255, 255])
    mascara = cv2.inRange(hsv, lower, upper)

    kernel = np.ones((5, 5), np.uint8)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)

    contornos, _ = cv2.findContours(
        mascara,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contornos:
        print(f"{ruta_imagen.name} -> No s'ha detectat cap skittle")
        return None

    contorno_skittle = seleccionar_contorn_skittle(contornos, imagen.shape)

    if contorno_skittle is None:
        print(f"{ruta_imagen.name} -> No s'ha trobat cap objecte circular valid")
        return None

    mascara_skittle = np.zeros(mascara.shape, dtype=np.uint8)
    cv2.drawContours(mascara_skittle, [contorno_skittle], -1, 255, -1)

    h_channel, s_channel, v_channel = cv2.split(hsv)

    mascara_color = cv2.bitwise_and(
        mascara_skittle,
        cv2.inRange(s_channel, 80, 255)
    )

    if cv2.countNonZero(mascara_color) < 50:
        mascara_color = mascara_skittle

    pixels_h = h_channel[mascara_color > 0]
    pixels_s = s_channel[mascara_color > 0]
    pixels_v = v_channel[mascara_color > 0]

    if len(pixels_h) == 0:
        print(f"{ruta_imagen.name} -> No s'han pogut obtenir pixels del skittle")
        return None

    h_median = float(np.median(pixels_h))
    s_median = float(np.median(pixels_s))
    v_median = float(np.median(pixels_v))

    color = clasificar_color_hsv(h_median, s_median, v_median)

    print(
        f"{ruta_imagen.name} -> {color} "
        f"(H={h_median:.1f}, S={s_median:.1f}, V={v_median:.1f})"
    )

    # Dibuixar deteccio
    x, y, w, h_rect = cv2.boundingRect(contorno_skittle)

    cv2.rectangle(
        imagen,
        (x, y),
        (x + w, y + h_rect),
        (0, 255, 0),
        2
    )

    cx = x + w // 2
    cy = y + h_rect // 2

    cv2.circle(
        imagen,
        (cx, cy),
        4,
        (0, 255, 0),
        -1
    )

    texto = f"{ruta_imagen.name}: {color}"

    cv2.putText(
        imagen,
        texto,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.imshow("Imatge detectada", imagen)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return color

# ============================================================
# MAIN
# ============================================================

def main():
    print("Carpeta actual:")
    print(CARPETA)
    print()

    if not IMAGENES:
        print("No s'han trobat imatges a la carpeta.")
        print("Extensions acceptades: .jpg, .jpeg, .png")
        return

    print("Imatges trobades:")
    for ruta in IMAGENES:
        print(" -", ruta.name)

    print()
    print("Resultats:")
    print("-" * 60)

    resultats = {}

    for ruta in IMAGENES:
        color = detectar_color_skittle(ruta)
        resultats[ruta.name] = color

    print()
    print("-" * 60)
    print("RESUM FINAL")
    print("-" * 60)

    for nom, color in resultats.items():
        print(f"{nom} -> {color}")


if __name__ == "__main__":
    main()