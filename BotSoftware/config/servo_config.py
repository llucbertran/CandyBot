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
DISPENSER_HOLD_S  = 0.05  # pause between the two moves
DISPENSER_GAP_S   = 0.2
DISPENSER_STEP    = 5     # degrees per step (lower = slower)
DISPENSER_STEP_MS = 0.01 # seconds between steps

DISPENSERS = {
    #         channel  rest  dispense
    "green":  {"channel": 0, "rest": 175, "dispense": 0},
    "orange": {"channel": 1, "rest": 175, "dispense": 0},
    "yellow": {"channel": 2, "rest": 175, "dispense": 0},
    "red":    {"channel": 3, "rest": 175, "dispense": 0},
    "purple": {"channel": 4, "rest":   0, "dispense": 175},  # inverted
}
