# Reload flow: the disk turns slowly and the camera watches it. Each quarter turn
# brings a new candy into view. When the camera reads a colour we wait a moment
# for the candy to reach the ramp, aim the ramp and update stock. If no candy
# shows up for two quarter turns the tray is empty and we stop.

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
    servo_controller.disk_start()
    count = 0
    last_candy = time.time()
    last_print = 0.0

    try:
        while True:
            if should_cancel and should_cancel():
                print("Reload cancelled.")
                break

            color = vision_controller.detect_color()
            now = time.time()

            if now - last_print >= cfg.DISK_QUARTER_S:
                print(f"  camera: {color or '-'}")
                last_print = now

            if color and now - last_candy >= cfg.DISK_CANDY_GAP_S:
                last_candy = now                    # reset the timer at detection
                time.sleep(cfg.DISK_RAMP_DELAY_S)   # let the candy reach the ramp
                servo_controller.ramp_to(color)
                total = candy_stock.add_candy(color, 1)
                count += 1
                print(f"  +1 {color} (total {total})")
                display.reloading(candy_stock.get_stock(), color)
                continue

            if now - last_candy >= cfg.DISK_EMPTY_TIMEOUT_S:
                print("Tray empty.")
                break

            time.sleep(cfg.CAMERA_INTERVAL_S)
    finally:
        servo_controller.disk_stop()
        servo_controller.ramp_center()

    display.reload_done(count)
    print(f"Reload done: {count} skittles.")
    return count


def reload_with_voice_cancel():
    """Reload while a background thread listens for a voice 'cancel'.

    Turn the crank during the reload and say "para" to stop early. The sorting
    finishes the current skittle, then stops."""
    cancel = threading.Event()
    done = threading.Event()

    def listen():
        while not cancel.is_set() and not done.is_set():
            if crank.is_turning():                       # user grabbed the crank
                response = api_client.record_and_send_while(crank.is_turning)
                if response.get("action") == "cancel":
                    cancel.set()
            time.sleep(0.1)

    threading.Thread(target=listen, daemon=True).start()
    try:
        return reload_once(should_cancel=cancel.is_set)
    finally:
        done.set()
