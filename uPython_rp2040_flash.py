from time import sleep
from machine import Pin

led = Pin(25, Pin.OUT)

while True:
    led.toggle()
    sleep(.5)
