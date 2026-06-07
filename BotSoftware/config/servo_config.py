# PCA9685 PWM board
PCA9685_ADDRESS  = 0x40
PCA9685_CHANNELS = 16

# SG90 servo parameters
SG90_RANGE     = 180
SG90_PULSE_MIN = 500   # µs at 0°
SG90_PULSE_MAX = 2500  # µs at 180°

# Ramp servo — TODO: assign channel after wiring
RAMP_CHANNEL      = 8
RAMP_CENTER_ANGLE = 90
RAMP_SETTLE_S     = 0.4

RAMP_ANGLES = {
    "red": 0, "orange": 45, "yellow": 90, "green": 135, "purple": 180,
}

# Disk servo (continuous 360°) — TODO: assign channel and calibrate times
DISK_CHANNEL        = 7
DISK_SPEED          = 0.30
DISK_CAMERA_PAUSE_S = 1.0

DISK_SEGMENTS_S = {
    "to_camera": 1.0, "to_ramp": 1.0, "to_recarga": 1.0,
}

# Dispenser servos — channels and angles confirmed on real hardware
DISPENSER_HOLD_S = 0.2
DISPENSER_GAP_S  = 0.3

DISPENSERS = {
    #         channel  rest  dispense
    "green":  {"channel": 0, "rest": 160, "dispense": 5},
    "purple": {"channel": 1, "rest": 160, "dispense": 5},
    "red":    {"channel": 2, "rest": 160, "dispense": 5},
    "orange": {"channel": 3, "rest": 160, "dispense": 5},
    "yellow": {"channel": 4, "rest": 160, "dispense": 5},
}
