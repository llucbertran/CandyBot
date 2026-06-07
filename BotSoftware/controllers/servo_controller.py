import time
from BotSoftware.config import servo_config as cfg

try:
    from adafruit_servokit import ServoKit
    _kit = ServoKit(channels=cfg.PCA9685_CHANNELS, address=cfg.PCA9685_ADDRESS)
    SIMULATION = False
except Exception as exc:
    _kit = None
    SIMULATION = True
    print(f"[servo] no hardware: {exc}")

_initialized = False


def _setup_sg90(channel):
    if SIMULATION:
        return
    servo = _kit.servo[channel]
    servo.actuation_range = cfg.SG90_RANGE
    servo.set_pulse_width_range(cfg.SG90_PULSE_MIN, cfg.SG90_PULSE_MAX)


def _set_angle(channel, angle):
    if SIMULATION:
        print(f"[servo] ch{channel} -> {angle} deg")
        return
    _kit.servo[channel].angle = angle


def _spin(channel, throttle, seconds):
    if SIMULATION:
        print(f"[servo] ch{channel} spin {seconds}s")
        return
    _kit.continuous_servo[channel].throttle = throttle
    time.sleep(seconds)
    _kit.continuous_servo[channel].throttle = 0


def _ensure_init():
    global _initialized
    if _initialized:
        return
    _setup_sg90(cfg.RAMP_CHANNEL)
    for d in cfg.DISPENSERS.values():
        _setup_sg90(d["channel"])
    _set_angle(cfg.RAMP_CHANNEL, cfg.RAMP_CENTER_ANGLE)
    for d in cfg.DISPENSERS.values():
        _set_angle(d["channel"], d["rest"])
    _initialized = True


def ramp_to(color):
    _ensure_init()
    _set_angle(cfg.RAMP_CHANNEL, cfg.RAMP_ANGLES[color])
    time.sleep(cfg.RAMP_SETTLE_S)


def ramp_center():
    _ensure_init()
    _set_angle(cfg.RAMP_CHANNEL, cfg.RAMP_CENTER_ANGLE)
    time.sleep(cfg.RAMP_SETTLE_S)


def disk_to_camera():
    _spin(cfg.DISK_CHANNEL, cfg.DISK_SPEED, cfg.DISK_SEGMENTS_S["to_camera"])
    time.sleep(cfg.DISK_CAMERA_PAUSE_S)


def disk_to_ramp():
    _spin(cfg.DISK_CHANNEL, cfg.DISK_SPEED, cfg.DISK_SEGMENTS_S["to_ramp"])


def disk_to_recarga():
    _spin(cfg.DISK_CHANNEL, cfg.DISK_SPEED, cfg.DISK_SEGMENTS_S["to_recarga"])


def dispense(color, qty=1):
    _ensure_init()
    d = cfg.DISPENSERS[color]
    for _ in range(qty):
        _set_angle(d["channel"], d["dispense"])
        time.sleep(cfg.DISPENSER_HOLD_S)
        _set_angle(d["channel"], d["rest"])
        time.sleep(cfg.DISPENSER_GAP_S)


if __name__ == "__main__":
    _ensure_init()
    for c in cfg.DISPENSERS:
        dispense(c, qty=1)
