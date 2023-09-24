from blink import blink

import time
import _thread
from ftp import ftpserver
import network

start_test_time = time.time()

def disconnect():
  sta_if = network.WLAN(network.STA_IF)
  if sta_if.isconnected():
    sta_if.active(False)
    blink(repeat = 2,speed = 0.5)
    print("WLAN disconnected")

  ap_if = network.WLAN(network.AP_IF)
  if ap_if.active():
    ap_if.active(False)
    blink(repeat = 2,speed = 0.5)
    print("Access Point disconnected")


def do_connect():
  global start_test_time
  start_test_time = time.time()

  sta_if = network.WLAN(network.STA_IF) #Connect to wifi
  if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    list = [names[0] for names in sta_if.scan()]
    if b'Jormungandr' in list:
      sta_if.connect('Jormungandr', 'PowerSnake')
    if b'De Rijke Huisjes' in list:
      sta_if.connect('De Rijke Huisjes', 'AAAAAAAAAA')

  ap_if = network.WLAN(network.AP_IF) #create accesspoint
  if not ap_if.active():
    ap_if.active(True)
    ap_if.config(essid='GhostShip')

  _thread.start_new_thread(test_connection, (sta_if,ap_if))

def test_connection(sta_if,ap_if):
  global start_test_time
  while not (sta_if.isconnected()):
    blink(repeat = 1)
    if time.time() > start_test_time + 20:
      blink(repeat = 2,speed = 0.5)
      break
    time.sleep(1)
  if sta_if.isconnected():
    print('network config:', sta_if.ifconfig())
    blink(repeat = 4,speed = 0.4)
    ftpserver()

  if sta_if.isconnected() or ap_if.active():
    blink(repeat = 6,speed = 0.2)
    start_webrepl()


def start_webrepl():
  import webrepl
  webrepl.start()
