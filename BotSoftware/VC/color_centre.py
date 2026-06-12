import cv2
import json
import pathlib
import numpy as np

# Small ROI slightly left of centre — where the candy slot passes
ROI_CX = 0.40   # centre x (fraction of frame width)
ROI_CY = 0.50   # centre y (fraction of frame height)
ROI_R  = 0.07   # half-size (fraction of frame width)

V_MIN    = 20    # below this → too dark → void (disco caught by hue filter, not by V alone)
SAT_VOID = 120   # below this → desaturated background → void  (empty slot S≈35)

# Disk surface hue filter (measured: H=152-167, S=120-175, V=60-115).
# Purple candy is at H=172 S=241, safely outside this zone on both H and S.
DISK_H_LO  = 148
DISK_H_HI  = 179
DISK_V_MAX = 130
DISK_SAT_MAX = 200

_CALIB_FILE = pathlib.Path(__file__).parent / "color_calibration.json"

_DEFAULTS = {
    # Hues measured from real camera output (RGB→HSV, ExposureTime≈5000):
    "green":  45,
    "yellow": 95,
    "orange": 121,
    "red":    135,
    "purple": 172,
}

DEBUG = True
_prev_log = object()


def _load_ref():
    if _CALIB_FILE.exists():
        try:
            data = json.loads(_CALIB_FILE.read_text())
            ref = {c: v["hue"] for c, v in data.items()}
            print("[vision] calibración: " + " ".join(f"{c}=H{v}" for c, v in ref.items()))
            return ref
        except Exception as e:
            print(f"[vision] error en calibración, usando defaults: {e}")
    print("[vision] sin calibración — corre calibrar_colores.py")
    return _DEFAULTS.copy()


REF_HUE = _load_ref()


def _hue_dist(a, b):
    d = abs(int(a) - int(b))
    return min(d, 180 - d)


def get_roi(frame):
    h, w = frame.shape[:2]
    cx, cy = int(w * ROI_CX), int(h * ROI_CY)
    r = int(w * ROI_R)
    return frame[max(0, cy - r):cy + r, max(0, cx - r):cx + r]


def detect(frame):
    """frame: RGB from camera. Returns (color_or_None, median_sat)."""
    roi = get_roi(frame)
    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    h_ch, s_ch, v_ch = cv2.split(hsv)

    med_h = int(np.median(h_ch))
    med_s = int(np.median(s_ch))
    med_v = int(np.median(v_ch))

    if med_h <= 12:
        result = None          # disk wrap-around (H≈0-12, same physical hue as H≈155-179)
        reason = "disco-L"
    elif DISK_H_LO <= med_h <= DISK_H_HI and med_v < DISK_V_MAX and med_s < DISK_SAT_MAX:
        result = None          # black disk surface (H≈148-179, medium-V, medium-S)
        reason = "disco-H"
    elif med_v < V_MIN:
        result = None          # too dark
        reason = "muy-oscuro"
    elif med_s < SAT_VOID:
        result = None          # empty slot — bright background through hole
        reason = "slot-vacío"
    else:
        result = min(REF_HUE, key=lambda c: _hue_dist(med_h, REF_HUE[c]))
        reason = f"H={med_h}"

    if DEBUG:
        global _prev_log
        if result != _prev_log or result is None:
            print(f"[vis] {result or 'void':7} | H={med_h:3d} S={med_s:3d} V={med_v:3d} ({reason})")
            _prev_log = result

    return result, med_s
