# Reload flow: bring each skittle to the camera, read its colour, route it to the
# right cylinder and update stock. Repeats until the tray is empty (no colour
# detected) or a cancel is requested.

import threading
import time

from BotSoftware.controllers import servo_controller, vision_controller
from BotSoftware.controllers import crank_controller as crank
from BotSoftware.controllers import display_controller as display
from BotSoftware.services import api_client
from BotSoftware.models import candy_stock


def reload_once(should_cancel=None):
    """Sort skittles until the tray is empty, or should_cancel() returns True.

    should_cancel is checked once per skittle (between candies)."""
    display.reloading_start()
    count = 0

    while True:
        if should_cancel and should_cancel():
            print("Reload cancelled.")
            break

        servo_controller.disk_to_camera()    # bring next skittle to the camera
        color = vision_controller.detect_color()

        if color is None:                     # nothing in view -> tray empty
            print("Tray empty.")
            break

        servo_controller.ramp_to(color)       # aim ramp at its cylinder
        servo_controller.disk_to_ramp()       # drop the skittle onto the ramp
        candy_stock.add_candy(color, 1)       # update stock
        servo_controller.ramp_center()
        servo_controller.disk_to_recarga()    # back to the start position

        count += 1
        print(f"  +1 {color}")
        display.reloading(candy_stock.get_stock(), color)

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
