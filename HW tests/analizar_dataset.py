# Reads the captured dataset and prints HSV stats per colour.
# Filters by saturation to isolate candy pixels from background.
#
# Usage:  python "HW tests/analizar_dataset.py"

import pathlib
import cv2
import numpy as np

FRAMES      = pathlib.Path(__file__).parent / "frames"
COLORS      = ["red", "orange", "yellow", "green", "purple"]
V_MIN       = 75
V_MAX       = 245
SAT_FILTERS = [0, 80, 120, 160]   # try different saturation floors


def get_pixels(folder, sat_min):
    hues, sats = [], []
    for p in sorted(folder.glob("*.jpg")):
        img = cv2.imread(str(p))
        if img is None:
            continue
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        mask = (v >= V_MIN) & (v <= V_MAX) & (s >= sat_min)
        if np.any(mask):
            hues.append(h[mask].flatten())
            sats.append(s[mask].flatten())
    if not hues:
        return None, None
    return np.concatenate(hues), np.concatenate(sats)


def pct(arr, p):
    return int(np.percentile(arr, p))


def show_table(sat_min):
    print(f"\n--- S >= {sat_min} ---")
    print(f"{'COLOR':8}  {'H_10':>4} {'H_25':>4} {'H_50':>4} {'H_75':>4} {'H_90':>4}   {'S_50':>4}   {'N_px':>8}")
    print("-" * 65)
    for color in COLORS + ["void"]:
        folder = FRAMES / color
        if not folder.exists():
            continue
        hues, sats = get_pixels(folder, sat_min)
        if hues is None or len(hues) == 0:
            print(f"{color:8}  (sin píxeles con S>={sat_min})")
            continue
        print(f"{color:8}  "
              f"{pct(hues,10):4d} {pct(hues,25):4d} {pct(hues,50):4d} "
              f"{pct(hues,75):4d} {pct(hues,90):4d}   "
              f"{pct(sats,50):4d}   {len(hues):8d}")


def main():
    for sat in SAT_FILTERS:
        show_table(sat)


if __name__ == "__main__":
    main()
