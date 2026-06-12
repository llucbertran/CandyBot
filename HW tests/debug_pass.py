# Debug: run one disk pass and print the real H/S/V of each candy in motion, so
# we can recalibrate the colour bands from reality instead of static holds.
# Run with a KNOWN candy order (cleanest: one colour at a time) and paste the
# output. Delete when done.
#   python "HW tests/debug_pass.py"

import sys
import time
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import cv2
import numpy as np
from BotSoftware.controllers import servo_controller, vision_controller
from BotSoftware.VC import camera_stream as cam

ROI = 0.40
V_MIN, V_MAX = 90, 245
S_CANDY = 95          # above the empty floor (~80), so we read the candy, not the floor
MIN_CANDY_PX = 1500   # this many saturated pixels means a candy is in view
SECONDS = 15

vision_controller.start()
servo_controller.disk_start()

t0 = time.time()
try:
    while time.time() - t0 < SECONDS:
        f = cam.capture_frame()
        h, w = f.shape[:2]
        rw, rh = int(w * ROI), int(h * ROI)
        x0, y0 = (w - rw) // 2, (h - rh) // 2
        hue, sat, val = cv2.split(cv2.cvtColor(f[y0:y0 + rh, x0:x0 + rw], cv2.COLOR_BGR2HSV))
        m = (val >= V_MIN) & (val <= V_MAX) & (sat >= S_CANDY)
        n = int(np.count_nonzero(m))
        if n >= MIN_CANDY_PX:
            print(f"H={np.median(hue[m]):3.0f}  S={np.median(sat[m]):3.0f}  V={np.median(val[m]):3.0f}  px={n}")
        time.sleep(0.03)
except KeyboardInterrupt:
    pass

servo_controller.disk_stop()
vision_controller.release()
