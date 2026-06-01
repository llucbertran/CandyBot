"""
Controlador de servos del CandyBot.

Llegeix TOTA la configuració de Software/config/servo_config.py i ofereix
funcions d'alt nivell perquè els altres controllers no toquin mai el hardware
directament:

    RAMPA      → ramp_to(color) / ramp_center()
    DISC 360°  → disk_to_camera() / disk_to_ramp() / disk_to_recarga()
    DISPENSERS → dispense(color, qty)

Funciona a la Raspberry Pi (PCA9685) i en mode SIMULACIÓ a qualsevol PC sense
hardware, per poder provar el flux sense trencar `python -m Software.main`.
"""

import time
from Software.config import servo_config as cfg

# ── Inicialització del hardware (segura fora de la Pi) ──────────────────────────
try:
    from adafruit_servokit import ServoKit
    _kit = ServoKit(channels=cfg.PCA9685_CHANNELS, address=cfg.PCA9685_ADDRESS)
    SIMULATION = False
except Exception as exc:  # sense I2C / sense llibreria → mode simulació
    _kit = None
    SIMULATION = True
    print(f"[servo] Mode SIMULACIO (sense hardware): {exc}")

_initialized = False


# ── Helpers de baix nivell ─────────────────────────────────────────────────────

def _setup_sg90(channel: int) -> None:
    """Configura el rang i els polsos d'un SG90."""
    if SIMULATION:
        return
    servo = _kit.servo[channel]
    servo.actuation_range = cfg.SG90_RANGE
    servo.set_pulse_width_range(cfg.SG90_PULSE_MIN, cfg.SG90_PULSE_MAX)


def _set_angle(channel: int, angle: int) -> None:
    """Mou un servo posicional (SG90) a un angle concret."""
    if SIMULATION:
        print(f"[sim] canal {channel} -> {angle} deg")
        return
    _kit.servo[channel].angle = angle


def _spin(channel: int, throttle: float, seconds: float) -> None:
    """Fa girar un servo de rotació contínua durant un temps i el frena."""
    if SIMULATION:
        print(f"[sim] canal {channel} gira {seconds}s a throttle {throttle}")
        return
    _kit.continuous_servo[channel].throttle = throttle
    time.sleep(seconds)
    _kit.continuous_servo[channel].throttle = 0


def _ensure_init() -> None:
    """Configura tots els servos i els porta a repòs (només un cop)."""
    global _initialized
    if _initialized:
        return

    _setup_sg90(cfg.RAMP_CHANNEL)
    for d in cfg.DISPENSERS.values():
        _setup_sg90(d["channel"])

    # Posicions de repòs inicials
    _set_angle(cfg.RAMP_CHANNEL, cfg.RAMP_CENTER_ANGLE)
    for d in cfg.DISPENSERS.values():
        _set_angle(d["channel"], d["rest"])

    _initialized = True
    print("[servo] Inicialitzat.")


# ═══════════════════════════════════════════════════════════════════════════════
# RAMPA
# ═══════════════════════════════════════════════════════════════════════════════

def ramp_to(color: str) -> None:
    """Apunta la rampa al dispenser del color indicat."""
    _ensure_init()
    angle = cfg.RAMP_ANGLES[color]
    _set_angle(cfg.RAMP_CHANNEL, angle)
    time.sleep(cfg.RAMP_SETTLE_S)


def ramp_center() -> None:
    """Torna la rampa a la posició central de repòs."""
    _ensure_init()
    _set_angle(cfg.RAMP_CHANNEL, cfg.RAMP_CENTER_ANGLE)
    time.sleep(cfg.RAMP_SETTLE_S)


# ═══════════════════════════════════════════════════════════════════════════════
# DISC 360°  (cicle: RECARGA → CAMERA → RAMPA → RECARGA)
# ═══════════════════════════════════════════════════════════════════════════════

def disk_to_camera() -> None:
    """Gira el disc des de RECARGA fins a CAMERA i s'atura per fer la foto."""
    _spin(cfg.DISK_CHANNEL, cfg.DISK_SPEED, cfg.DISK_SEGMENTS_S["to_camera"])
    time.sleep(cfg.DISK_CAMERA_PAUSE_S)


def disk_to_ramp() -> None:
    """Gira el disc des de CAMERA fins a RAMPA (deixa caure el candy)."""
    _spin(cfg.DISK_CHANNEL, cfg.DISK_SPEED, cfg.DISK_SEGMENTS_S["to_ramp"])


def disk_to_recarga() -> None:
    """Gira el disc des de RAMPA fins a RECARGA (tanca el cicle)."""
    _spin(cfg.DISK_CHANNEL, cfg.DISK_SPEED, cfg.DISK_SEGMENTS_S["to_recarga"])


# ═══════════════════════════════════════════════════════════════════════════════
# DISPENSERS
# ═══════════════════════════════════════════════════════════════════════════════

def dispense(color: str, qty: int = 1) -> None:
    """
    Allibera `qty` candies del dispenser del color indicat.
    Cada candy = rest → dispense → rest. L'invertit funciona sol pels seus angles.
    """
    _ensure_init()
    d = cfg.DISPENSERS[color]

    for i in range(qty):
        _set_angle(d["channel"], d["dispense"])
        time.sleep(cfg.DISPENSER_HOLD_S)
        _set_angle(d["channel"], d["rest"])
        time.sleep(cfg.DISPENSER_GAP_S)


# ── Prova manual directa (guia: control_servo_basic.py) ─────────────────────────
if __name__ == "__main__":
    _ensure_init()

    print("\n-> Provant RAMPA (cada dispenser + centre)")
    for c in cfg.COLORS:
        ramp_to(c)
    ramp_center()

    print("\n-> Provant DISC 360 (cicle complet)")
    disk_to_camera()
    disk_to_ramp()
    disk_to_recarga()

    print("\n-> Provant DISPENSERS (2 candies cadascun)")
    for c in cfg.COLORS:
        dispense(c, qty=2)

    print("\nFet.")
