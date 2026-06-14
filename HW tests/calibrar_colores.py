# Calibracion interactiva de color.
# Mide el void (slot vacio), el disco negro y cada color de caramelo, y guarda
# las referencias de hue en BotSoftware/VC/color_calibration.json.
# Si los avisos lo indican, ajusta V_MIN / SAT_VOID en color_centre.py.
#
# Uso:  python "HW tests/calibrar_colores.py"

import sys
import json
import time
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import cv2
import numpy as np
from BotSoftware.VC import camera_stream as cam
from BotSoftware.VC.color_centre import get_roi, ROI_CX, ROI_CY, ROI_R, V_MIN, SAT_VOID

COLORS   = ["red", "orange", "yellow", "green", "purple"]
OUT_FILE = pathlib.Path(__file__).resolve().parents[1] / "BotSoftware/VC/color_calibration.json"
SAMPLE_S = 1.5


def sample(label):
    """Captura ~1.5s de frames y devuelve la mediana H, S, V del ROI."""
    hs, ss, vs = [], [], []
    t0 = time.time()
    while time.time() - t0 < SAMPLE_S:
        frame = cam.capture_frame()
        roi   = get_roi(frame)
        hsv   = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        hs.append(int(np.median(h)))
        ss.append(int(np.median(s)))
        vs.append(int(np.median(v)))
        time.sleep(0.03)
    med_h = int(np.median(hs))
    med_s = int(np.median(ss))
    med_v = int(np.median(vs))
    print(f"    H={med_h:3d}  S={med_s:3d}  V={med_v:3d}  ({len(hs)} frames)")
    return med_h, med_s, med_v


def live_preview():
    """Muestra una lectura instantanea del ROI."""
    frame = cam.capture_frame()
    roi   = get_roi(frame)
    hsv   = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    print(f"  [live] H={int(np.median(h)):3d}  S={int(np.median(s)):3d}  V={int(np.median(v)):3d}")


def main():
    print("=== Calibracion de colores ===")
    print(f"ROI: x={ROI_CX:.0%}  y={ROI_CY:.0%}  radio={ROI_R:.0%} del frame")
    print(f"Umbrales actuales: V_MIN={V_MIN}  SAT_VOID={SAT_VOID}\n")

    cam.start()
    calib = {}

    try:
        # Void (slot vacio / fondo)
        input("Sin caramelos, sin disco. Pulsa Enter para medir el VOID (slot vacio)...")
        live_preview()
        vh, vs_v, vv = sample("void")
        print(f"  void: H={vh} S={vs_v} V={vv}")
        if vs_v >= SAT_VOID:
            print(f"  [AVISO] S_void={vs_v} >= SAT_VOID={SAT_VOID}: ajusta SAT_VOID en color_centre.py")
        print()

        # Disco (superficie negra del disco)
        input("Pon la superficie negra del disco bajo el ROI. Pulsa Enter para medir el DISCO...")
        live_preview()
        dh, ds, dv = sample("disk")
        print(f"  disco: H={dh} S={ds} V={dv}")
        if dv >= 130:
            print(f"  [AVISO] V_disco={dv} alto: revisa el filtro de disco en color_centre.py")
        print()

        # Colores de caramelo
        for color in COLORS:
            while True:
                input(f"Pon {color.upper()} en la zona del ROI y pulsa Enter...")
                live_preview()
                h, s, v = sample(color)
                if s < SAT_VOID:
                    print(f"  [AVISO] S={s} < SAT_VOID={SAT_VOID}: este caramelo se detectaria como void")
                ans = input(f"  H={h} S={s} V={v}  OK? (Enter=si / n=repetir): ").strip().lower()
                if ans != "n":
                    calib[color] = {"hue": h, "sat": s, "val": v}
                    print()
                    break

    finally:
        cam.release()

    OUT_FILE.write_text(json.dumps(calib, indent=2))
    print(f"Guardado en {OUT_FILE.name}:")
    print(f"  {'color':8}  H    S    V")
    for c, v in calib.items():
        print(f"  {c:8}  {v['hue']:3d}  {v['sat']:3d}  {v['val']:3d}")
    print("\nAhora corre test_ordenar.py: el detector usara estos valores.")


if __name__ == "__main__":
    main()
