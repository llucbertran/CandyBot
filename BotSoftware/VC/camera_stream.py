# Persistent camera using picamera2. 

import time
import cv2
from picamera2 import Picamera2

CAMERA_SIZE = (640, 480)     # under the 700px the detector downscales to, so it's fast
WARMUP_S    = 1.5            # let exposure and white balance settle before locking

EXPOSURE_US = 25000
GAIN        = 4.0
FRAME_US    = 33333          # lock the camera to ~30 fps

# Fix white balance so hues don't drift between runs.
# Set to None to let AWB settle during warmup (prints the gains so you can copy them here).
# Once you have stable gains from a good run, paste them: e.g. (1.8, 1.5)
FIXED_COLOUR_GAINS = None

_camera = None


def start():
    global _camera
    if _camera is not None:
        return
    cam = Picamera2()
    # CAMBIO CRÍTICO: Usar BGR888 para que OpenCV lo entienda nativamente y vaya más rápido.
    cam.configure(cam.create_preview_configuration(
        main={"format": "BGR888", "size": CAMERA_SIZE},
        controls={"AeEnable": False, "ExposureTime": EXPOSURE_US, "AnalogueGain": GAIN,
                  "FrameDurationLimits": (FRAME_US, FRAME_US)}))
    cam.start()
    time.sleep(WARMUP_S)
    if FIXED_COLOUR_GAINS is not None:
        cam.set_controls({"AwbEnable": False, "ColourGains": FIXED_COLOUR_GAINS})
        print(f"[cam] ColourGains fijos: {FIXED_COLOUR_GAINS}")
    else:
        gains = cam.capture_metadata().get("ColourGains")
        if gains:
            cam.set_controls({"AwbEnable": False, "ColourGains": gains})
        print(f"[cam] ColourGains congelados en: {gains}  ← copia este valor en FIXED_COLOUR_GAINS")
    _camera = cam


def capture_frame():
    """Return the latest frame as a BGR array (ready for OpenCV)."""
    if _camera is None:
        start()
    
    # 1. Obtenemos el frame desde Picamera2. 
    # Por defecto, este suele venir en formato RGB.
    frame = _camera.capture_array()
    
    # 2. CAMBIO CRÍTICO: OpenCV trabaja en BGR. 
    # Si no convertimos, el Rojo y el Azul se intercambian.
    bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    return bgr_frame


def release():
    global _camera
    if _camera is not None:
        _camera.stop()
        _camera.close()
        _camera = None