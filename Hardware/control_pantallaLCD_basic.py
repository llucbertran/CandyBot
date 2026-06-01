from RPLCD.i2c import CharLCD
from time import sleep
# Res de accents

lcd = CharLCD('PCF8574', 0x3F)  # Cambia a 0x3F si no funciona

# Escribir solo en la fila superior (fila 0)
lcd.cursor_pos = (0, 0)  # (columna, fila)
lcd.write_string('Hola')

# Escribir solo en la fila inferior (fila 1)
lcd.cursor_pos = (1, 0)
lcd.write_string('Robot')

sleep(2)

# Borrar solo una fila
lcd.cursor_pos = (1, 0)
lcd.write_string('CandyBot')  # 16 espacios
