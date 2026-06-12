# Pulls frames from the persistent camera and reads the candy colour from the
# centre of the frame. Returns red/orange/yellow/green/purple, or None.

try:
    from BotSoftware.VC import camera_stream
    from BotSoftware.VC.color_centre import detect as classify_frame
    SIMULATION = False
except Exception as exc:
    SIMULATION = True
    print(f"[vision] no hardware: {exc}")


def start():
    """Open and warm up the camera before sorting starts."""
    if not SIMULATION:
        camera_stream.start()


def detect_color():
    """Capture one frame and return red/orange/yellow/green/purple, or None."""
    if SIMULATION:
        return None
    return classify_frame(camera_stream.capture_frame())


def release():
    """Release the camera when sorting is done."""
    if not SIMULATION:
        camera_stream.release()
