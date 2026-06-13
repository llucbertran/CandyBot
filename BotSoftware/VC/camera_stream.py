# Persistent camera using picamera2.

import time
import cv2
from picamera2 import Picamera2

CAMERA_SIZE = (640, 480)     # under the 700px the detector downscales to, so it's fast
WARMUP_S    = 1.5            # let exposure and white balance settle before locking

EXPOSURE_US = 25000
GAIN        = 4.0
FRAME_US    = 33333          # lock the camera to ~30 fps

# Fix the white balance so hues don't drift between runs. Leave as None to let
# the AWB settle during warmup and print the gains; once you have a good run,
# paste those gains here, e.g. (1.8, 1.5).
FIXED_COLOUR_GAINS = None

_camera = None


def start():
    global _camera
    if _camera is not None:
        return
    cam = Picamera2()
    cam.configure(cam.create_preview_configuration(
        main={"format": "BGR888", "size": CAMERA_SIZE},
        controls={"AeEnable": False, "ExposureTime": EXPOSURE_US, "AnalogueGain": GAIN,
                  "FrameDurationLimits": (FRAME_US, FRAME_US)}))
    cam.start()
    time.sleep(WARMUP_S)
    if FIXED_COLOUR_GAINS is not None:
        cam.set_controls({"AwbEnable": False, "ColourGains": FIXED_COLOUR_GAINS})
        print(f"[cam] fixed ColourGains: {FIXED_COLOUR_GAINS}")
    else:
        gains = cam.capture_metadata().get("ColourGains")
        if gains:
            cam.set_controls({"AwbEnable": False, "ColourGains": gains})
        print(f"[cam] frozen ColourGains: {gains} (paste into FIXED_COLOUR_GAINS to lock)")
    _camera = cam


def capture_frame():
    """Return the latest camera frame as a NumPy array for OpenCV."""
    if _camera is None:
        start()
    frame = _camera.capture_array()
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)


def release():
    global _camera
    if _camera is not None:
        _camera.stop()
        _camera.close()
        _camera = None
