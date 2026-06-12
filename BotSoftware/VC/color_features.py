import cv2
import numpy as np

V_MIN = 75
V_MAX = 245


def extract(roi_bgr):
    """Features from a standard BGR ROI (camera native format).

    Call with:
      - inference: roi cropped directly from camera frame (BGR)
      - training:  cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
                   to undo the R/B swap introduced by capturar_dataset.py
    Both paths produce identical standard HSV values.
    """
    h_img, w_img = roi_bgr.shape[:2]
    total = h_img * w_img

    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    hue, sat, val = cv2.split(hsv)

    bright = (val >= V_MIN) & (val <= V_MAX)
    n = int(np.count_nonzero(bright))

    if n > 0:
        hues = hue[bright].astype(np.float32)
        sats = sat[bright].astype(np.float32)
        hist, _ = np.histogram(hues, bins=36, range=(0, 180))
        hist_norm = hist.astype(np.float32) / n
        med_s  = float(np.median(sats)) / 255
        std_h  = float(np.std(hues))    / 90
    else:
        hist_norm = np.zeros(36, dtype=np.float32)
        med_s = 0.0
        std_h = 0.0

    return list(hist_norm) + [n / total, med_s, std_h]
