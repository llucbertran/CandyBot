import cv2
import json
import pathlib
import numpy as np

# Small ROI slightly left of centre, where the candy slot passes.
ROI_CX = 0.40   # centre x (fraction of frame width)
ROI_CY = 0.50   # centre y (fraction of frame height)
ROI_R  = 0.07   # half-size (fraction of frame width)

V_MIN    = 20    # below this the ROI is too dark to be a candy
SAT_VOID = 120   # below this it is the empty slot (bright background, low saturation)

# Black disk surface. Its hue sits in a known band with medium value and
# saturation, so candies (which are brighter and more saturated) fall outside it.
DISK_H_LO    = 148
DISK_H_HI    = 179
DISK_V_MAX   = 130
DISK_SAT_MAX = 200

_CALIB_FILE = pathlib.Path(__file__).parent / "color_calibration.json"

# Reference hues measured from the real camera output.
_DEFAULTS = {
    "green":  45,
    "yellow": 95,
    "orange": 121,
    "red":    135,
    "purple": 172,
}

DEBUG = False
_prev_log = object()


def _load_ref():
    if _CALIB_FILE.exists():
        try:
            data = json.loads(_CALIB_FILE.read_text())
            ref = {c: v["hue"] for c, v in data.items()}
            print("[vision] calibration loaded: " + " ".join(f"{c}=H{v}" for c, v in ref.items()))
            return ref
        except Exception as e:
            print(f"[vision] calibration error, using defaults: {e}")
    print("[vision] no calibration found, run calibrar_colores.py")
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
    """Classify the candy in the ROI. Returns (color_or_None, median_sat)."""
    roi = get_roi(frame)
    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    h_ch, s_ch, v_ch = cv2.split(hsv)

    med_h = int(np.median(h_ch))
    med_s = int(np.median(s_ch))
    med_v = int(np.median(v_ch))

    if med_h <= 12:
        result, reason = None, "disk-low"          # disk hue wrapped around 0
    elif DISK_H_LO <= med_h <= DISK_H_HI and med_v < DISK_V_MAX and med_s < DISK_SAT_MAX:
        result, reason = None, "disk"              # black disk surface
    elif med_v < V_MIN:
        result, reason = None, "dark"
    elif med_s < SAT_VOID:
        result, reason = None, "empty"             # empty slot
    else:
        result = min(REF_HUE, key=lambda c: _hue_dist(med_h, REF_HUE[c]))
        reason = f"H={med_h}"

    if DEBUG:
        global _prev_log
        if result != _prev_log or result is None:
            print(f"[vis] {result or 'void':7} | H={med_h:3d} S={med_s:3d} V={med_v:3d} ({reason})")
            _prev_log = result

    return result, med_s
