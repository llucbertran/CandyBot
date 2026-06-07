# HW test: crank / reed switch.
# Turn the crank and watch ON (cranking) / OFF (stopped).
# Use it to check the wiring and tune REED_PIN / IDLE_TIMEOUT in crank_controller.py.
#   python "HW tests/test_palanca.py"

import sys
import time
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from BotSoftware.controllers import crank_controller as crank

print("Turn the crank (Ctrl-C to quit)...")
while True:
    crank.wait_for_turn()
    print("ON  - cranking")
    while crank.is_turning():
        time.sleep(0.1)
    print("OFF - stopped")
