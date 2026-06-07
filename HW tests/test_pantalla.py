# HW test: 16x2 character LCD (HD44780 over PCF8574).
# Cycles through every screen so we can check the panel on the bench.
#   python "HW tests/test_pantalla.py"

import sys
import time
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from BotSoftware.controllers import display_controller as display

demo_stock = {"green": 12, "purple": 5, "red": 20, "orange": 8, "yellow": 14}

screens = [
    lambda: display.idle(),
    lambda: display.listening(),
    lambda: display.dispensing("taronja", 3),
    lambda: display.served(),
    lambda: display.reloading_start(),
    lambda: display.reloading(demo_stock, "red"),
    lambda: display.low_stock("groc", 1),
    lambda: display.reload_done(42),
]

for screen in screens:
    screen()
    time.sleep(2)

display.clear()
