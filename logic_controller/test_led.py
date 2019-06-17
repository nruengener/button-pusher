import time

from interfaces.led import led_control

led_control("green", "on")
# led_control("red", "on")

time.sleep(2)
led_control("green", "flash")
# led_control("red", "flash")

time.sleep(4)

led_control("green", "heartbeat")

time.sleep(4)

led_control("green", "off")
# led_control("red", "off")


