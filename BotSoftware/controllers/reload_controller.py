# Reload flow: the disk turns slowly and the camera watches the ROI at 30 fps.
# A colour must appear in two consecutive frames before it counts (eliminates
# stray false positives). Armed/disarmed logic ensures each slot is counted once.

import threading
import time

from BotSoftware.config import servo_config as cfg
from BotSoftware.controllers import servo_controller, vision_controller
from BotSoftware.controllers import crank_controller as crank
from BotSoftware.controllers import display_controller as display
from BotSoftware.services import api_client
from BotSoftware.models import candy_stock


def reload_once(should_cancel=None):
    """Sort skittles until the tray is empty, or should_cancel() returns True."""
    display.reloading_start()
    vision_controller.start()
    servo_controller.disk_start()

    count      = 0
    armed      = True
    last_seen  = time.time()
    prev_color = None

    try:
        while True:
            if should_cancel and should_cancel():
                print("Reload cancelled.")
                break

            result = vision_controller.detect_color()
            color  = result[0] if result else None
            now    = time.time()

            if color is not None and color == prev_color:
                # Two consecutive frames agree: real candy
                last_seen = now
                if armed:
                    armed = False
                    print(f"  [detect] {color}")
                    time.sleep(cfg.DISK_RAMP_DELAY_S)
                    servo_controller.ramp_to(color)
                    total = candy_stock.add_candy(color, 1)
                    count += 1
                    print(f"  +1 {color}  (total {total})")
                    display.reloading(candy_stock.get_stock(), color)
            else:
                if now - last_seen >= cfg.DISK_REARM_S:
                    armed = True
                if now - last_seen >= cfg.DISK_EMPTY_TIMEOUT_S:
                    print("Tray empty.")
                    break

            prev_color = color

    finally:
        servo_controller.disk_stop()
        servo_controller.ramp_center()
        vision_controller.release()

    display.reload_done(count)
    print(f"Reload done: {count} skittles.")
    return count


def reload_with_voice_cancel():
    """Reload while a background thread listens for a voice 'cancel'."""
    cancel = threading.Event()
    done   = threading.Event()

    def listen():
        while not cancel.is_set() and not done.is_set():
            if crank.is_turning():
                response = api_client.record_and_send_while(crank.is_turning)
                if response.get("action") == "cancel":
                    cancel.set()
            time.sleep(0.1)

    threading.Thread(target=listen, daemon=True).start()
    try:
        return reload_once(should_cancel=cancel.is_set)
    finally:
        done.set()
