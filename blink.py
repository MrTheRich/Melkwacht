import machine
import os
import _thread
import time

led = machine.Pin(21, machine.Pin.OUT)

blinking = 0

def blink_thread(speed):
  global blinking
  while blinking != 0:
    led.on()
    time.sleep(0.1 * speed)
    blinking -= 1
    led.off()
    time.sleep(0.4 * speed)

def blink(start = True, repeat = -1, speed = 1.0):
  global blinking
  if start and blinking == 0:
    blinking = repeat
    _thread.start_new_thread(blink_thread, (1.0,))
  elif not start and blinking != 0:
    blinking = 0

