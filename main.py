import machine
import random
import utime as time
import _thread
from machine import Pin, SPI, ADC, Timer
import gc9a01
import vga1_8x16 as font
import NotoSerif_32 as fontbig
import buzzer
from math import sqrt,pow
import wlan

SENSOR_BALANCE_1 = 99 #Ohm
SENSOR_BALANCE_2 = 99 #Ohm
SENSOR_BALANCE_3 = 99 #Ohm
COEF_A = 0.0039083
COEF_B = -0.0000005775
RES_FREEZING_POINT = 100 #Ohm at 0°C
RES_BOILING_POINT = 138.5 #Ohm at 100°C
TEMP_POLL_TIME = 3000 #miliseconds

class State:
  display = 1
  ftp=1
  button = 0
  run = True
  last_press_time = 0
  temperature = 22.0
  last_update = 0
  next_action = None
  ftp_on = False
  sensor1 = 0.0 # Yellow bottom of rod Celcius
  sensor2 = 0.0 # Orange bottom of rod Celcius
  sensor3 = 0.0 # Grey 75cm from bottom Celcius
  reference = 3.3 # Overall voltage

def main():

  button_pin = Pin(16, Pin.IN, Pin.PULL_DOWN) # 17 control button
  ftp_pin = Pin(15, Pin.IN, Pin.PULL_UP) # 0 control button on chip

  display_pin = Pin(17, Pin.OUT) # 16 turn on off display backlight
  display_pin(State.display)

  display = gc9a01.GC9A01(
    SPI(2, baudrate=80000000, polarity=1, sck=Pin(18), mosi=Pin(23)),
    240,
    240,
    cs=Pin(14, Pin.OUT), # select module
    reset=Pin(33, Pin.OUT), # Reset
    dc=Pin(27, Pin.OUT), # data/command
    backlight=display_pin,
    buffer_size=64*64*2
    )
  display.init()

  print("display initiated")

  #display.vline(120, 120, 100, gc9a01.WHITE)

  led = Pin(21, Pin.OUT) # 2 led on devboard

  def poll_sensors():
    sensor_toggle(True)
    time.sleep_ms(20)

    reference_samples = 0
    samples1 = 0
    samples2 = 0
    samples3 = 0

    for _ in range(10):
      samples1 += sensor1.read_uv()
      samples2 += sensor2.read_uv()
      samples3 += sensor3.read_uv()
      reference_samples += reference.read_uv()
      time.sleep_ms(1)

    State.reference = reference_samples/10.0 #Average Voltage
    State.sensor1 = mvolt_to_temp(samples1/10.0,SENSOR_BALANCE_1) #Celcius
    State.sensor2 = mvolt_to_temp(samples2/10.0,SENSOR_BALANCE_2) #Celcius
    State.sensor3 = mvolt_to_temp(samples3/10.0,SENSOR_BALANCE_3) #Celcius

    sensor_toggle(False)

  def init_poll(call):
    _thread.start_new_thread(poll_sensors, ())

  sensor_toggle = Pin(19, Pin.OUT)
  sensor_toggle(False)
  sensor1 = ADC(36) # Yellow bottom of rod
  sensor2 = ADC(34) # Orange bottom of rod
  sensor3 = ADC(32) # Grey 75cm from bottom
  reference = ADC(39) # Overall voltage
  sensor_timer = Timer(0)
  sensor_timer.init(period=TEMP_POLL_TIME, callback=init_poll)

  def mvolt_to_temp(temp_volt, balance_resistor):
    ratio = 1 - (float(temp_volt) / float(State.reference))

    if ratio == 0.0:
        print ("No Sensor connected")
        return 0.0

    rtd_resistance = balance_resistor / ratio - balance_resistor

    if COEF_B == 0.0:
        print ("Coefficient B is zero")
        return 0.0
    if RES_FREEZING_POINT == 0.0:
        print ("RES_FREEZING_POINT is zero")
        return 0.0

    temp = (-COEF_A + sqrt(COEF_A**2 - 4*COEF_B(1-rtd_resistance/RES_FREEZING_POINT)))/(2*COEF_B)
    return temp

  def toggle_display():
    print("Toggling on display")
    display_pin(1 - State.display)
    State.display = 1 - State.display

  def button_double_press(pin):
    State.run = not State.run
    if State.run:
      time.sleep_ms(100)
      _thread.start_new_thread(update, ())

  def button_press(pin):
    if pin() and State.button != pin():
      dt = time.ticks_ms() - State.last_press_time
      print(dt)

      if dt < 80:
        print("Canceled")
        return
      elif dt < 200: #if double clicked
        State.next_action = None
        print("DoubleClick")
        button_double_press(pin)
      else:
        print("Cick")
        State.next_action = toggle_display #schedule action
        _thread.start_new_thread(do_action, ())

      led.on()
      State.last_press_time = time.ticks_ms()

    else:
      led.off()
    State.button = pin()

  def ftp_press(pin):
    print("FTP Toggle")
    if pin():
      if State.ftp:
        wlan.disconnect()
      else:
        wlan.do_connect()
      State.ftp = 1 - State.ftp


  button_pin.irq(button_press) #interupt for button
  ftp_pin.irq(ftp_press) #interupt for ftp

  display.fill(0)

  State.last_update = time.ticks_ms()

  def do_action():
    #execute action if not double click
    time.sleep_ms(200)
    if State.next_action != None:
      State.next_action()
      State.next_action = None


  def update():
    while State.run:

      temp = (State.sensor1 + State.sensor2)/2.0
      s = f"{temp:.1f}C"
      l = display.write_len(fontbig, s)//2

      display.fill(0)
      display.text(
        font,
        "Huidige Temperatuur:",
        40,
        120-16-32,
        gc9a01.WHITE,
        gc9a01.BLACK
      )

      display.write(
        fontbig,
        s,
        120-l,
        120-16,
        gc9a01.WHITE,
        gc9a01.BLACK
      )

      if time.ticks_ms() >= State.last_update + 300:
        State.temperature -= 0.1
        State.last_update += 300
      time.sleep_ms(12)

  _thread.start_new_thread(update, ())

main()
