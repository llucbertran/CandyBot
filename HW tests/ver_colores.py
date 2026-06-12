# Gira el disco y muestra los valores HSV del ROI + clasificación en tiempo real.
# Usa esto para verificar umbrales y hues de referencia.
#
# Uso:  python "HW tests/ver_colores.py"
# Ctrl+C para parar.

import sys
import time
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import cv2
import numpy as np
from BotSoftware.VC import camera_stream as cam
from BotSoftware.VC.color_centre import (
    get_roi, V_MIN, SAT_VOID,
    DISK_H_LO, DISK_H_HI, DISK_V_MAX, DISK_SAT_MAX,
    REF_HUE, _hue_dist,
)

from BotSoftware.controllers import servo_controller

INTERVAL_S = 0.10   # segundos entre lecturas (10 Hz)


def read_roi():
    frame = cam.capture_frame()
    roi   = get_roi(frame)
    hsv   = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    return int(np.median(h)), int(np.median(s)), int(np.median(v))


def classify(h, s, v):
    if DISK_H_LO <= h <= DISK_H_HI and v < DISK_V_MAX and s < DISK_SAT_MAX:
        return "DISCO  "
    if v < V_MIN:
        return "oscuro "
    if s < SAT_VOID:
        return "void   "
    color = min(REF_HUE, key=lambda c: _hue_dist(h, REF_HUE[c]))
    return f"={color:<6}"


def main():
    cam.start()
    servo_controller.disk_start()
    print(f"Umbrales: V_MIN={V_MIN}  SAT_VOID={SAT_VOID}  "
          f"DISCO H=[{DISK_H_LO},{DISK_H_HI}] V<{DISK_V_MAX} S<{DISK_SAT_MAX}")
    print(f"Hues ref: { {c: v for c, v in REF_HUE.items()} }")
    print(f"{'#':>4}  {'clasif':8}  {'H':>3}  {'S':>3}  {'V':>3}")
    print("-" * 36)

    i = 0
    try:
        while True:
            h, s, v = read_roi()
            tag = classify(h, s, v)
            print(f"{i:4d}  {tag}  {h:3d}  {s:3d}  {v:3d}")
            i += 1
            time.sleep(INTERVAL_S)
    except KeyboardInterrupt:
        pass
    finally:
        servo_controller.disk_stop()
        cam.release()
        print("\nParado.")


if __name__ == "__main__":
    main()
