# PCA9685 PWM board
PCA9685_ADDRESS  = 0x40
PCA9685_CHANNELS = 16

# SG90 servo parameters
SG90_RANGE     = 180
SG90_PULSE_MIN = 500   # µs at 0°
SG90_PULSE_MAX = 2500  # µs at 180°

# Ramp servo — channel 6
RAMP_CHANNEL      = 6
RAMP_CENTER_ANGLE = 90
RAMP_SETTLE_S     = 0.4

RAMP_ANGLES = {
    "green":  38,
    "orange": 138,
    "yellow": 0,
    "red":    88,
    "purple": 178,
}

# Sorting disk (continuous 360°, 4 holes every 90°). It turns slowly and the
# camera reads each candy as it passes. The times below derive from how long
# one quarter turn takes, so calibrating DISK_QUARTER_S adjusts the whole flow.
DISK_CHANNEL         = 7
DISK_SPEED           = 0.20   # low continuous throttle; the sign sets direction
DISK_QUARTER_S       = 2.0    # approx time to rotate one quarter (calibrate)
DISK_RAMP_DELAY_S    = DISK_QUARTER_S - DISK_QUARTER_S / 3   # wait after detecting before aiming the ramp
DISK_CANDY_GAP_S     = DISK_QUARTER_S / 2   # ignore re-reads of the candy just handled
DISK_EMPTY_TIMEOUT_S = DISK_QUARTER_S * 2   # no candy for this long -> tray empty
CAMERA_INTERVAL_S    = 0.1    # time between photos

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
