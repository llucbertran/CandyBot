from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16, address=0x40)
kit.servo[0].actuation_range = 180
kit.servo[0].set_pulse_width_range(500, 2500)

for ang in [0, 90, 180, 90]:
    kit.servo[0].angle = ang
    print("angulo", ang)
    time.sleep(2)
