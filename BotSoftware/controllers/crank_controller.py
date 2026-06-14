# Reed switch on a GPIO. Turning the crank moves a magnet past it -> pulses.
# First pulse after idle  = crank started -> start recording.
# No pulses for IDLE_TIMEOUT = crank stopped -> stop recording and send audio.

import time

REED_PIN     = 17     # BCM pin wired to the reed switch
IDLE_TIMEOUT = 2.0    # seconds without pulses -> crank considered stopped
BOUNCE_S     = 0.01   # reed switch debounce
POLL_S       = 0.05
SIM_TURN_S   = 4.0    # simulated cranking duration when there's no hardware

try:
    from gpiozero import Button
    _reed = Button(REED_PIN, pull_up=True, bounce_time=BOUNCE_S)
    SIMULATION = False
except Exception as exc:
    _reed = None
    SIMULATION = True
    print(f"[crank] no hardware: {exc}")

_last_pulse = 0.0


def _on_pulse():
    global _last_pulse
    _last_pulse = time.time()


if not SIMULATION:
    _reed.when_pressed = _on_pulse


def is_turning():
    """True while pulses keep arriving (crank still moving)."""
    window = SIM_TURN_S if SIMULATION else IDLE_TIMEOUT
    return time.time() - _last_pulse < window


def wait_for_turn():
    """Block until the crank starts turning."""
    global _last_pulse
    if SIMULATION:
        print("[crank] (sim) cranking started")
        _last_pulse = time.time()
        return
    while not is_turning():
        time.sleep(POLL_S)
