import cv2
import numpy as np
import subprocess
from pathlib import Path
import tempfile
import argparse
import time

CARPETA = Path(__file__).parent


def capturar_imagen_rpicam(timeout_ms=1, width=None, height=None):
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        ruta_tmp = Path(tmp.name)

    cmd = ['rpicam-still', '--immediate', '-n', '-o', str(ruta_tmp)]

    if timeout_ms is not None:
        cmd += ['-t', str(timeout_ms)]
    if width is not None:
        cmd += ['--width', str(width)]
    if height is not None:
        cmd += ['--height', str(height)]

    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True)
        if resultado.returncode != 0:
            print('Error capturant amb rpicam-still:')
            if resultado.stderr:
                print(resultado.stderr.strip())
            return None

        datos = np.fromfile(str(ruta_tmp), dtype=np.uint8)
        imagen = cv2.imdecode(datos, cv2.IMREAD_COLOR)
        return imagen
    except Exception as error:
        print(f'Error executant rpicam-still: {error}')
        return None
    finally:
        try:
            ruta_tmp.unlink(missing_ok=True)
        except Exception:
            pass


def clasificar_color_hsv(h, s, v):
    if v < 45:
        return 'molt fosc / ombra'
    if s < 45 and v > 150:
        return 'blanc / gris clar'
    if (h < 20 or h >= 170) and v < 130 and s < 180:
        return 'marro'
    if h < 10 or h >= 170:
        return 'vermell'
    if 10 <= h < 24:
        return 'taronja'
    if 24 <= h < 40:
        return 'groc'
    if 40 <= h < 85:
        return 'verd'
    if 85 <= h < 130:
        return 'blau'
    if 130 <= h < 160:
        return 'lila'
    if 160 <= h < 170:
        return 'rosa / vermell clar'
    return 'color desconegut'


def seleccionar_contorn_skittle(contornos, shape):
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
        toca_vora = x <= marge or y <= marge or x + w >= ancho - marge or y + h >= alto - marge
        if toca_vora:
            continue

        ratio = w / h if h != 0 else 0
        if ratio < 0.55 or ratio > 1.45:
            continue

        cx = x + w / 2
        cy = y + h / 2
        distancia_centre = np.sqrt((cx - centre_imatge_x) ** 2 + (cy - centre_imatge_y) ** 2)
        distancia_normalitzada = distancia_centre / np.sqrt(ancho ** 2 + alto ** 2)
        score = area * circularitat * (1 - distancia_normalitzada)

        if score > millor_score:
            millor_score = score
            millor_contorn = contorno

    return millor_contorn


def detectar_color_skittle_desde_array(imagen, mostrar=True):
    if imagen is None:
        return None, None

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

    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return None, imagen

    contorno_skittle = seleccionar_contorn_skittle(contornos, imagen.shape)
    if contorno_skittle is None:
        return None, imagen

    mascara_skittle = np.zeros(mascara.shape, dtype=np.uint8)
    cv2.drawContours(mascara_skittle, [contorno_skittle], -1, 255, -1)

    h_channel, s_channel, v_channel = cv2.split(hsv)
    mascara_color = cv2.bitwise_and(mascara_skittle, cv2.inRange(s_channel, 80, 255))

    if cv2.countNonZero(mascara_color) < 50:
        mascara_color = mascara_skittle

    pixels_h = h_channel[mascara_color > 0]
    pixels_s = s_channel[mascara_color > 0]
    pixels_v = v_channel[mascara_color > 0]

    if len(pixels_h) == 0:
        return None, imagen

    h_median = float(np.median(pixels_h))
    s_median = float(np.median(pixels_s))
    v_median = float(np.median(pixels_v))
    color = clasificar_color_hsv(h_median, s_median, v_median)

    vis = imagen.copy()
    x, y, w, h_rect = cv2.boundingRect(contorno_skittle)
    cv2.rectangle(vis, (x, y), (x + w, y + h_rect), (0, 255, 0), 2)
    cx = x + w // 2
    cy = y + h_rect // 2
    cv2.circle(vis, (cx, cy), 4, (0, 255, 0), -1)
    texto = f"{color} | H={h_median:.1f} S={s_median:.1f} V={v_median:.1f}"
    cv2.putText(vis, texto, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    return color, vis


def main():
    parser = argparse.ArgumentParser(description='Captura continua amb rpicam-still --immediate i detecta el color del skittle')
    parser.add_argument('--width', type=int, default=None)
    parser.add_argument('--height', type=int, default=None)
    parser.add_argument('--timeout', type=int, default=1, help='Temps de captura en ms per rpicam-still')
    parser.add_argument('--interval', type=float, default=0.2, help='Temps entre captures en segons')
    parser.add_argument('--solo-cambios', action='store_true', help='Només imprimeix quan canvia el color detectat')
    args = parser.parse_args()

    ultimo_color = object()

    try:
        while True:
            t0 = time.perf_counter()
            imagen = capturar_imagen_rpicam(timeout_ms=args.timeout, width=args.width, height=args.height)
            t1 = time.perf_counter()
            color, vis = detectar_color_skittle_desde_array(imagen)
            t2 = time.perf_counter()

            texto_color = color if color is not None else 'no_detectado'
            if (not args.solo_cambios) or (texto_color != ultimo_color):
                print(
                    f'Resultado={texto_color} | captura={t1 - t0:.3f}s | deteccion={t2 - t1:.3f}s | total={t2 - t0:.3f}s',
                    flush=True
                )
                ultimo_color = texto_color

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print('\nDetingut per usuari.')
    finally:
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
