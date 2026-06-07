# HW test: sorting mechanism (disk + camera + ramp + dispensers).
# Sorts skittles into their cylinders until the tray is empty.
# No voice / mic involved — just the hardware loop.
#   python "HW tests/test_ordenar.py"

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from BotSoftware.controllers.reload_controller import reload_once
from BotSoftware.models import candy_stock

if __name__ == "__main__":
    candy_stock.set_all(0)   # start the test from a known stock
    try:
        reload_once()
    finally:
        candy_stock.reset()    # leave the DB empty again
