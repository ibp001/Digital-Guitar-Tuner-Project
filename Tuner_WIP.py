#   ECEG 201 Final Application Project
#   Author: Izzy Philosophe
#   Application: Guitar Tuner
#
#   Inputs:
#       - Electric Guitar
#            - guitar -> guitar amplifier -> 3.5mm audio jack adapter -> pinout to feather analogIO
#       - Adafruit ulab API for signal data processing

#---------------------- Library Imports ---------------------------

import time
import board
from analogio import AnalogIn
import math
from neopixelFunctions import *
import rtc
import busio
from digitalio import DigitalInOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import neopixel
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

# Utilizes Adafruit's ulab API for CircuitPython
import ulab
import ulab.numerical




#------------------ Preliminary Initializations and Setup ----------------------


analog_in = AnalogIn(board.A1)

abs_max = 0
abs_min = 0
ptp = 0
avg = 0

# test out the RTC feature of the Feahter M4
clock = rtc.RTC()

# Choose "home" or "Bucknell"
location = "home"

# Get wifi details and more from a secrets.py file
# Determine if the location is home or Bucknell
if location == "home":
    try:
        from secrets import secrets_home
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise
    secrets = secrets_home
else:
    try:
        from secrets import secrets_Bucknell
    #    secrets = secrets_Bucknell
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise
    secrets = secrets_Bucknell

TEXT2_URL = "http://api.thingspeak.com/channels/1221440/fields/field1/last.txt"
TEXT2_URL2 = "http://api.thingspeak.com/channels/1221440/fields/field2/last.txt"

# create the I2C object which will be used to talk to the motor and sensor
i2c = busio.I2C(board.SCL, board.SDA)

# If you have an AirLift Featherwing or ItsyBitsy Airlift:
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp)

# create the stepper motor object
kit = MotorKit(i2c=i2c)
# The Portescap S26M048 series stepper motors have 48 steps per revolution
# https://media.digikey.com/pdf/Data%20Sheets/Portescap%20Danaher%20PDFs/26M048B.pdf
# We will use "interleave" mode which doubles the number of steps for a full revolution
motor_steps = 2038
full_rev = motor_steps
# define the starting point of the motor as 0
motorPos = 0
# define the max position of the motor for RH of 100%
# this number is based on the position of the physical stop peg on the enclosure.  That point
# is defined as 0 or the min, and that point mirrored about the vertical axis is defined
# as the max.  The max is about 84% of a full rotation.
maxMotor = round(0.84*full_rev)

dial_left_pos = 510
dial_right_pos = 1020
dial_center_pos = 765


# Designated open-string notes and their frequencies (Hz):
E2 = 82

E2_A2_midpoint = 94.7

A2 = 110

A2_D3_midpoint = 126.6

D3 = 147

D3_G3_midpoint = 169.8

G3 = 196

G3_B3_midpoint = 220

B3 = 247

B3_E4_midpoint = 285.1

E4 = 330


# define the pin used to control the NeoPixel ring
pixel_pin = board.D5
# The number of NeoPixels
# Our NeoPixel ring is based on the SK6812
# https://cdn-shop.adafruit.com/product-files/1138/SK6812+LED+datasheet+.pdf
num_pixels = 24
# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
ORDER = neopixel.GRB
# create the NeoPixel ring object
pixel = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=True, pixel_order=ORDER)




#-------------------- Functions ---------------------------


# The wheel function turns an integer from 0 to 255 to a 3 element vector color value.
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixel[i] = wheel(pixel_index & 255)
        pixel.show()
        time.sleep(wait)


def get_voltage(pin):
    return (pin.value * 3.3) / 65536
    #return pin.value


def analyze(array):
    abs_max = max(array)
    abs_min = min(array)
    ptp = abs_max - abs_min
    avg = sum(array) / len(array)
    print("max: ", abs_max, "V")
    print("min: ", abs_min, "V")
    print("ptp: ", ptp, "V")
    print("avg: ", avg, "V")
    print("size: ", len(array), '\n')


def smooth(array):
    avg = float(sum(array) / len(array))
    for x in range(len(array)):
        array[x] = (array[x] - avg)
        array[x] = array[x] * 5


def stretch(array):
    avg = float(sum(array) / len(array))
    for x in range(len(array)):
        scalar = (float(array[x] / avg))**2
        array[x] = array[x] * scalar


def smooth2(array):
    # variable for holding undersampling rate
    undersample = 3

    for x in range(0, len(array), undersample):
        if (x + undersample) > (len(array) - 1):
            undersample -= (len(array) - 1)
        delta = array[x + undersample] - array[x]
        if delta != 0:
            for y in range(1, undersample):
                array[x + y] = array[x] + (y/delta)


def get_freq(array):
    abs_max = max(array)
    abs_min = min(array)
    ptp = abs_max - abs_min
    avg = float(sum(array) / len(array))
    if (array[0] < 0):
        below = True
        freq = 0
    else:
        below = False
        freq = 1
    #up = True
    for x in range(len(array)):
        #print((x,))
        #time.sleep(0.01)
        if (below and (array[x] >= avg)):
            freq = freq + 1
            below = False
        if (array[x] < (avg - (ptp*.333))):
            below = True
    return freq


#def display_freq(frequency):




#--------------------- Final Initialization-------------------------------


# pause to make sure everything is copacetic
time.sleep(1)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
#print("Firmware vers.", esp.firmware_version)
#print("MAC addr:", [hex(i) for i in esp.MAC_address])

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except RuntimeError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))

# esp._debug = True
r = requests.get(TEXT2_URL)
print("")
print("Maker-E outside temperature right now is", r.text, "°F.")
print("Double this value is ", float(r.text) * 2)
print("-" * 40)
r.close()

print("Done!")
print(clock.datetime)

# run this code once to initialize the device and make sure NeoPixels and motor are working
# light up red, then pause
pixel.fill((255, 0, 0))
time.sleep(0.5)
# light up green, then pause
pixel.fill((0, 255, 0))
time.sleep(0.5)
# light up blue, then pause
pixel.fill((0, 0, 255))
time.sleep(0.5)
# run through a rainbox cycle once on the NeoPixels
rainbow_cycle(0.001)  # rainbow cycle with 1ms delay per step
# turn off the NeoPixels
pixel.fill((0, 0, 0))
time.sleep(0.5)

# home the motor by making it perform a full revolution counterclockwise until it hits the stop peg
# we're using terminals M1 and M2 on the FeatherWing board so we need stepper1
for i in range(full_rev):
    kit.stepper1.onestep(style=stepper.SINGLE, direction=stepper.BACKWARD)
    time.sleep(0.01) # give the device time to catch up between steps

#initiallizing the LEDS
ring = get_ring()
bar_graph((255, 0, 0), 11, True, 3, ring, False)
bar_graph((255, 100, 0), 10, True, 4, ring, False)
bar_graph((255, 255, 0), 9, True, 5, ring, False)
bar_graph((0, 255, 0), 8, True, 6, ring, False)
bar_graph((255, 255, 255), 22, True, 16, ring, False)
time.sleep(2)
print("")




#------------------------------- Main Loop --------------------------------------


flag = False
while flag:

    # samples the audio voltage signal for .25 seconds and stores it all in a list
    wave = []
    current_time = time.monotonic_ns()
    while ((time.monotonic_ns() - current_time) < 250000000):
    #for x in range(256):
        wave.append(get_voltage(analog_in))
        #time.sleep(0.0005)
    sample_time = .25 * (2048/len(wave))
    while len(wave) > 2048:
        wave.pop(len(wave)-1)

    #stretch(wave)
    #smooth(wave)
    #smooth2(wave)

    uwave = ulab.array(wave)
    #a, b = ulab.fft.fft(uwave)
    fft = ulab.fft.fft(uwave)

    #a[:71] = 0
    #a[441:] = 0
    #b[:71] = 0
    #b[441:] = 0

    #fft[0][:70] = 0
    #fft[1][:70] = 0
    #fft[0][441:] = 0
    #fft[1][441:] = 0


    #smoothed, imag = ulab.fft.ifft(a, b)
    #smoothed = ulab.fft.ifft(fft[0], fft[1])

    #print(len(wave), len(smoothed), len(a), len(b))

    #for x in range(2048):
        #print((wave[x], smoothed[0][x]))
        #print((wave[x],))
        #print((fft[0][x],))
        #time.sleep(0.05)

    for x in range(70, 441):
        print((fft[0][x],))
        time.sleep(0.05)

    print(len(fft[0]))
    time.sleep(3)
    #print((fft[0],))

    #print(get_freq(smoothed[0]) * 4)
    #print("frequency is ", ulab.numerical.argmax(fft[0][70:441]))

    #time.sleep(1)
    #flag = False