"""
═══════════════════════════════════════════════════════════════════════════════
 CONFIGURACIÓ CENTRAL DE TOTS ELS SERVOS DEL CANDYBOT
═══════════════════════════════════════════════════════════════════════════════

Hardware:
  - Placa PWM PCA9685 (16 canals) controlada via adafruit_servokit.ServoKit
  - 1 × servo DISC 360° (Futaba S3003 mod.)  → rotació contínua
  - 1 × servo RAMPA (SG90)                   → posicional
  - 5 × servos DISPENSER (SG90)              → posicional

═══════════════════════════════════════════════════════════════════════════════
"""

# ── Placa PWM PCA9685 ──────────────────────────────────────────────────────────
PCA9685_ADDRESS = 0x40
PCA9685_CHANNELS = 16

# ── Paràmetres físics d'un SG90 ────────────────────────────────────────────────
SG90_RANGE = 180          # graus de recorregut
SG90_PULSE_MIN = 500      # µs (0°)
SG90_PULSE_MAX = 2500     # µs (180°)

# Colors oficials, en ordre físic dels dispensers
COLORS = ["red", "orange", "yellow", "green", "purple"]


# ═══════════════════════════════════════════════════════════════════════════════
# 1) SERVO RAMPA (SG90) — dirigeix el candy cap al dispenser correcte
#    Sempre torna al CENTRE després de cada operació (repòs ≈ -90..+90 → 90°).
# ═══════════════════════════════════════════════════════════════════════════════
RAMP_CHANNEL = 1
RAMP_CENTER_ANGLE = 90       # posició de repòs (sempre torna aquí)
RAMP_SETTLE_S = 0.4          # temps perquè el servo arribi i el candy caigui

# Angle de la rampa per a cada dispenser, repartits en ~180°.
# (primer = 0°, últim = 180°)
RAMP_ANGLES = {
    "red":    0,
    "orange": 45,
    "yellow": 90,
    "green":  135,
    "purple": 180,
}


# ═══════════════════════════════════════════════════════════════════════════════
# 2) SERVO DISC 360° (Futaba S3003 mod.) — rotació CONTÍNUA
#    No té posició absoluta → es controla amb VELOCITAT (throttle) + TEMPS.
#    Cicle físic:  RECARGA → CAMERA → RAMPA → RECARGA
#    CALIBRAR els temps cronometrant el robot real.
# ═══════════════════════════════════════════════════════════════════════════════
DISK_CHANNEL = 0
DISK_SPEED = 0.30               # throttle [-1.0 .. 1.0]; el signe marca el sentit
DISK_CAMERA_PAUSE_S = 1.0       # pausa a CAMERA perquè la càmera faci la foto

# Segons de gir entre dues parades consecutives.
DISK_SEGMENTS_S = {
    "to_camera":  1.0,    # des de RECARGA fins a CAMERA
    "to_ramp":    1.0,    # des de CAMERA  fins a RAMPA
    "to_recarga": 1.0,    # des de RAMPA   fins a RECARGA (tanca el cicle)
}


# ═══════════════════════════════════════════════════════════════════════════════
# 3) DISPENSERS (5 × SG90) — solten candies un a un
#    Una operació = rest → dispense → rest  (= 1 candy alliberat).
#    Per dispensar N candies es repeteix l'operació N vegades.
#
#    El dispenser "purple" està INVERTIT: fa el moviment al revés.
# ═══════════════════════════════════════════════════════════════════════════════
DISPENSER_HOLD_S = 0.35         # temps a l'angle de soltada
DISPENSER_GAP_S = 0.25          # pausa entre candies consecutius

DISPENSERS = {
    #  color        canal   rest   dispense
    "red":    {"channel": 2, "rest": 0,   "dispense": 60},
    "orange": {"channel": 3, "rest": 0,   "dispense": 60},
    "yellow": {"channel": 4, "rest": 0,   "dispense": 60},
    "green":  {"channel": 5, "rest": 0,   "dispense": 60},
    "purple": {"channel": 6, "rest": 180, "dispense": 120},  # HARDWARE INVERTIT
}
