# 16x2 character LCD over a PCF8574 I2C backpack (HD44780).
# The rest of the code calls the semantic screens below, so swapping the
# panel later only means rewriting this file.

import time

LCD_ADDRESS = 0x3F
LCD_COLS = 16
LCD_ROWS = 2

LOW_STOCK_HOLD_S = 3   # keep the "not enough stock" message on screen this long

# Custom glyphs stored in the LCD's CGRAM (5x8 pixels each).
_GLYPHS = {
    0: (0x00, 0x0E, 0x1F, 0x1F, 0x1F, 0x0E, 0x00, 0x00),  # candy
    1: (0x00, 0x0A, 0x0A, 0x00, 0x11, 0x0E, 0x00, 0x00),  # smiley
    2: (0x00, 0x0A, 0x1F, 0x1F, 0x0E, 0x04, 0x00, 0x00),  # heart
    3: (0x00, 0x04, 0x06, 0x1F, 0x06, 0x04, 0x00, 0x00),  # arrow
}
CANDY, SMILEY, HEART, ARROW = "\x00", "\x01", "\x02", "\x03"

# Readable fallbacks when running without hardware.
_PLAIN = str.maketrans({CANDY: "o", SMILEY: ":)", HEART: "<3", ARROW: ">"})

try:
    from RPLCD.i2c import CharLCD
    _lcd = CharLCD("PCF8574", LCD_ADDRESS, cols=LCD_COLS, rows=LCD_ROWS)
    for slot, bitmap in _GLYPHS.items():
        _lcd.create_char(slot, bitmap)
    SIMULATION = False
except Exception as exc:
    _lcd = None
    SIMULATION = True
    print(f"[lcd] no hardware: {exc}")


def _fit(text):
    return text.ljust(LCD_COLS)[:LCD_COLS]


def show(line1="", line2=""):
    if SIMULATION:
        print(f"[lcd] {line1.translate(_PLAIN)} | {line2.translate(_PLAIN)}")
        return
    _lcd.cursor_pos = (0, 0)
    _lcd.write_string(_fit(line1))
    _lcd.cursor_pos = (1, 0)
    _lcd.write_string(_fit(line2))


# Screens

def idle():
    show("CandyBot " + CANDY, "Gira la maneta")


def listening():
    show("Escoltant...", ARROW + " Parla ara")


def dispensing(color, qty):
    dots = CANDY * min(qty, 5)
    show("Dispensant:", f"{qty}x {color} {dots}")


def served():
    show("Gaudeix! " + SMILEY, "Bon profit " + HEART)


def empty_command():
    show("No t'he entes", "Torna-ho a dir")


def low_stock(color, available):
    show("Stock insufic.", f"{color} max: {available}")
    time.sleep(LOW_STOCK_HOLD_S)


def reloading_start():
    show("Recarrega " + CANDY, "Gira per omplir")


def reloading(stock, last_color):
    total = sum(stock.values())
    n = stock.get(last_color, 0)
    show(f"Total: {total}", f"+1 {last_color} ({n})")


def reload_done(count):
    show("Recarrega fi " + SMILEY, f"{count} skittles")


def message(title, subtitle=""):
    show(title, subtitle)


def clear():
    if SIMULATION:
        print("[lcd] clear")
    else:
        _lcd.clear()
