# Captures one camera frame (via BotSoftware/VC) and returns the skittle colour
# mapped to one of the 5 candy colours. Returns None when there's no skittle.

_COLOR_MAP = {
    "vermell": "red",
    "taronja": "orange",
    "groc":    "yellow",
    "verd":    "green",
    "lila":    "purple",
}

try:
    import cv2  # noqa: F401  (only to check vision deps are present)
    SIMULATION = False
except Exception as exc:
    SIMULATION = True
    print(f"[vision] no hardware: {exc}")


def detect_color():
    """Capture one frame and return red/orange/yellow/green/purple, or None."""
    if SIMULATION:
        return None
    from BotSoftware.VC.detectar_colors_rpicam import (
        capturar_imagen_rpicam,
        detectar_color_skittle_desde_array,
    )
    image = capturar_imagen_rpicam()
    raw = detectar_color_skittle_desde_array(image, mostrar=False)
    return _COLOR_MAP.get(raw)
