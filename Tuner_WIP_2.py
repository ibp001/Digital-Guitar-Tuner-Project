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






#------------------ Preliminary Initializations and Setup ----------------------


analog_in = AnalogIn(board.A1)

#abs_max = 0
#abs_min = 0
#ptp = 0
#avg = 0

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

dial_left_pos = 480
dial_right_pos = 1180
dial_center_pos = 830


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
#pixel_pin = board.D5
# The number of NeoPixels
# Our NeoPixel ring is based on the SK6812
# https://cdn-shop.adafruit.com/product-files/1138/SK6812+LED+datasheet+.pdf
num_pixels = 24
# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
ORDER = neopixel.GRB
# create the NeoPixel ring object
#pixel = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=True, pixel_order=ORDER)




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


def set_motor_pos(pos, current_motor_pos):
    # define an updated motor arm position based on RH
    newMotorPos = int(pos)
    # see if there is a change in motor arm position
    delta = newMotorPos - current_motor_pos
    # if there is a change in motor arm position then move the arm
    if delta != 0:
        if (delta) > 0:
            for i in range(delta):
                kit.stepper1.onestep(style=stepper.SINGLE, direction=stepper.FORWARD)
                time.sleep(0.01) # give the device time to catch up between steps
        if (delta) < 0:
            for i in range(abs(delta)):
                kit.stepper1.onestep(style=stepper.SINGLE, direction=stepper.BACKWARD)
                time.sleep(0.01) # give the device time to catch up between steps
    # update the current motor arm position
    return newMotorPos


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
    return


def stretch_and_center(array):
    #avg = float(sum(array) / len(array))
    #for x in range(len(array)):
        #array[x] = array[x]/avg
    avg = float(sum(array) / len(array))
    for x in range(len(array)):
        array[x] = (array[x] - avg)
    return array


def stretch(array):
    avg = float(sum(array) / len(array))
    for x in range(len(array)):
        scalar = (float(array[x] / avg))**2
        array[x] = array[x] * scalar
    return


def smooth2(array):
    # variable for holding undersampling rate
    undersample = 3

    for x in range(0, len(array), undersample):
        if (x + undersample) > (len(array) - 1):
            undersample -= (len(array) - 1)
        delta_ = array[x + undersample] - array[x]
        if delta_ != 0:
            for y in range(1, undersample):
                array[x + y] = array[x] + (y/delta_)

    return array


def get_freq(array, sample_time):
    threshold = 0.1
    abs_max = max(array)
    abs_min = min(array)
    ptp = abs_max - abs_min
    avg = float(sum(array) / len(array))
    maxxes = 0
    mins = 0
    avgs = 0
    on_max = False
    on_min = False
    on_avg = False
    if array[0] >= (abs_max * (1.0 - threshold)):
        on_max = True
        maxxes += 1
    elif array[0] <= (abs_min * (1.0 + threshold)):
        on_min = True
        mins += 1
    elif (array[0] >= (avg * (1.0 - threshold))) and (array[0] <= (avg * (1.0 + threshold))):
        on_avg = True
        avgs += 1
    for x in range(len(array)):
        if array[x] >= (abs_max * (1.0 - threshold)):
            if not on_max:
                on_max = True
                on_min = False
                on_avg = False
                maxxes += 1
        elif array[x] <= (abs_min * (1.0 + threshold)):
            if not on_min:
                on_max = False
                on_min = True
                on_avg = False
                mins += 1
        elif (array[x] >= (avg * (1.0 - threshold))) and (array[x] <= (avg * (1.0 + threshold))):
            if not on_avg:
                on_max = False
                on_min = False
                on_avg = True
                avgs += 1
        else:
            on_max = False
            on_min = False
            on_avg = False

    print('maxxes: ', maxxes, '\n')
    print('mins: ', mins, '\n')
    print('avgs: ', avgs, '\n')
    freq = min(maxxes, mins, avgs) / sample_time
    #freq = ((maxxes + mins + avgs)/3) / sample_time
    #freq = (avgs/2) / sample_time
    return freq

def get_freq_zeroed(array, sample_time):
    threshold = 0.05
    abs_max = max(array)
    abs_min = min(array)
    ptp = abs_max - abs_min
    #avg = float(sum(array) / len(array))
    maxxes = 0
    mins = 0
    avgs = 0
    on_max = False
    on_min = False
    on_avg = False
    if array[0] >= (abs_max * (1.0 - threshold)):
        on_max = True
        maxxes += 1
    elif array[0] <= (abs_min * (1.0 - threshold)):
        on_min = True
        mins += 1
    elif (array[0] >= (abs_min * threshold)) and (array[0] <= (abs_max * threshold)):
        on_avg = True
        avgs += 1
    for x in range(len(array)):
        if array[x] >= (abs_max * (1.0 - threshold)):
            if not on_max:
                on_max = True
                on_min = False
                on_avg = False
                maxxes += 1
        elif array[x] <= (abs_min * (1.0 - threshold)):
            if not on_min:
                on_max = False
                on_min = True
                on_avg = False
                mins += 1
        elif (array[x] >= (abs_min * threshold)) and (array[x] <= (abs_max * threshold)):
            if not on_avg:
                on_max = False
                on_min = False
                on_avg = True
                avgs += 1
        #else:
            #on_max = False
            #on_min = False
            #on_avg = False

    print('maxxes: ', maxxes, '\n')
    print('mins: ', mins, '\n')
    print('avgs: ', avgs, '\n')
    freq = min(maxxes, mins, avgs) / sample_time
    return freq

def get_freq_correlation(wave, time_delta):
    length = len(wave)
    sample_size = 512
    threshold = 0.1
    #start = int((length - sample_size) / 2)
    #start = 0
    #end = int((length + sample_size) / 2)
    #end = 512
    uwave = ulab.array(wave)
    correlation = ulab.filter.convolve(uwave, ulab.numerical.flip(uwave[0:512]))
    match = ulab.numerical.max(correlation)
    match_location = ulab.numerical.argmax(correlation)
    #time.sleep(3)
    #print("match requirement: ", match, '\n')
    #print("highest match location: ", match_location, '\n')
    #print("correlation length: ", len(correlation), '\n')
    #time.sleep(3)
    #for x in correlation:
        #print((x,))
        #time.sleep(0.01)
    #first = False
    local_max = []
    local_max.clear()
    count = 0
    #start = 0
    #while correlation[count] != match:
    #    count += 1
    #start = count
    while correlation[match_location + count] >= (match * (1.0 - threshold)):
        #start += 1
        count += 1
        if (match_location + count) == len(correlation):
            return 0.0
    while correlation[match_location + count] < (match * (1.0 - threshold)):
        #start += 1
        count += 1
        if (match_location + count) == len(correlation):
            return 0.0
    start = count
    #print
    while correlation[match_location + count] >= (match * (1.0 - threshold)):
        #start += 1
        local_max.append(correlation[match_location + count])
        count += 1
        if (match_location + count) == len(correlation):
            return 0.0
    second_peak = ulab.numerical.argmax(local_max)
    #print("peak within local_max: ", second_peak, '\n')
    period = float((second_peak + start) * time_delta)
    #print("correlation period : ", period, '\n')
    frequency = float(1/period)
    if period == 0:
        frequency = None
    return frequency
    #return (1 / (((ulab.numerical.argmax(local_max) + start) - match_location) * time_delta))

    #for x in range(match_location + count, len(correlation)):
        #if correlation[x] >= (match * (1.0 - threshold)):
            #period = float((x-match_location) * time_delta)
            #print("correlation period : ", period, '\n')
            #frequency = float(1/period)
            #if period == 0:
                #frequency = None
            #return frequency
    #return correlation
    #return (1 / (len(correlation) - match_location))

def display_freq(frequency, current_motor_pos):

    if (frequency >= 71) and (frequency < E2_A2_midpoint):
        bar_graph((255, 255, 255), 22, True, 16, ring, False)
        set_pixel((0, 255, 0), 21)
        newMotorPos = set_motor_pos((dial_center_pos +(350*((12/2.5)*math.log(freq/E2, 2)))), current_motor_pos)
    elif (frequency >= E2_A2_midpoint) and (frequency < A2_D3_midpoint):
        bar_graph((255, 255, 255), 22, True, 16, ring, False)
        set_pixel((0, 255, 0), 20)
        newMotorPos = set_motor_pos((dial_center_pos +(350*((12/2.5)*math.log(freq/A2, 2)))), current_motor_pos)
    elif (frequency >= A2_D3_midpoint) and (frequency < D3_G3_midpoint):
        bar_graph((255, 255, 255), 22, True, 16, ring, False)
        set_pixel((0, 255, 0), 19)
        newMotorPos = set_motor_pos((dial_center_pos +(350*((12/2.5)*math.log(freq/D3, 2)))), current_motor_pos)
    elif (frequency >= D3_G3_midpoint) and (frequency < G3_B3_midpoint):
        bar_graph((255, 255, 255), 22, True, 16, ring, False)
        set_pixel((0, 255, 0), 18)
        newMotorPos = set_motor_pos((dial_center_pos +(350*((12/2.5)*math.log(freq/G3, 2)))), current_motor_pos)
    elif (frequency >= G3_B3_midpoint) and (frequency < B3_E4_midpoint):
        bar_graph((255, 255, 255), 22, True, 16, ring, False)
        set_pixel((0, 255, 0), 17)
        newMotorPos = set_motor_pos((dial_center_pos +(350*((12/2.5)*math.log(freq/B3, 2)))), current_motor_pos)
    elif (frequency >= B3_E4_midpoint) and (frequency < 381):
        bar_graph((255, 255, 255), 22, True, 16, ring, False)
        set_pixel((0, 255, 0), 16)
        newMotorPos = set_motor_pos((dial_center_pos +(350*((12/2.5)*math.log(freq/E4, 2)))), current_motor_pos)
    else:
        bar_graph((255, 255, 255), 22, True, 16, ring, False)
        newMotorPos = current_motor_pos
    return newMotorPos

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
#pixel.fill((255, 0, 0))
#time.sleep(0.5)
# light up green, then pause
#pixel.fill((0, 255, 0))
#time.sleep(0.5)
# light up blue, then pause
#pixel.fill((0, 0, 255))
#time.sleep(0.5)
# run through a rainbox cycle once on the NeoPixels
#rainbow_cycle(0.001)  # rainbow cycle with 1ms delay per step
# turn off the NeoPixels
#pixel.fill((0, 0, 0))
#time.sleep(0.5)

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

top_freq = 0
#flag = False
flag = True
while flag:

    #print('taking sample in 3')
    #time.sleep(1)
    #print('2')
    #time.sleep(1)
    #print('1')
    #time.sleep(1)
    #print('starting sample now \n')

    #sample_time = .25
    power = 2048
    #time_step = 0.0005
    # samples the audio voltage signal for .25 seconds and stores it all in a list
    wave = []
    wave.clear()
    start_time = time.monotonic_ns()
    #while ((time.monotonic_ns() - current_time) < (1000000000 * sample_time)):
    for x in range(power):
        wave.append(get_voltage(analog_in))
        #time.sleep(time_step)
    end_time = time.monotonic_ns()

    total_time = float((end_time - start_time)/1000000000)
    #print('total sample time: ', total_time, '\n')
    time_step = float(total_time/power)
    #print('time step between samples: ', time_step, '\n')
    #time.sleep(5)

    #for x in range(power):
        #print((wave[x],))
        #time.sleep(0.01)
    #time.sleep(5)

    #print((wave,))
    #time.sleep(5)

    #power = 1
    #while len(wave) >= power:
    #    power = power * 2
    #power = power / 2
    #print('power of 2 needed: ', power, '\n')

    #total_time = float(sample_time * (power/len(wave)))
    #print('total sample time: ', total_time)
    #time_step = float(total_time/power)
    #print('time step between samples: ', time_step, '\n')

    #print('number of samples before cut: ', len(wave))
    #while len(wave) > power:
    #    wave.pop(len(wave)-1)
    #print('number of samples after cut: ', len(wave), '\n')
    #time.sleep(5)

    #stretch(wave)
    #smooth(wave)
    #smooth2(wave)

    #print(freq)
    #stretch_and_center(wave)
    #freq = get_freq(wave, total_time)
    freq = get_freq_correlation(stretch_and_center(wave), time_step)
    print('frequency: ', freq, '\n')

    #if freq > top_freq:
    #    top_freq = freq

    #if freq == 0:
    #    top_freq = 0

    #print('frequency: ', top_freq, '\n')

    #uwave = ulab.array(wave)
    #reverse = ulab.numerical.flip(uwave)
    #convoluted = ulab.filter.convolve(uwave, reverse)
    #print((convoluted,))
    #print(ulab.numerical.max(convoluted))
    #print(ulab.numerical.argmax(convoluted))
    #print(len(convoluted))
    #time.sleep(5)

    #print("frequency is ", , '\n')
    #a, b = ulab.fft.fft(uwave)
    #fft = ulab.fft.spectrogram(uwave)
    #get_freq_2(uwave)

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

    #for x in range(power):
        #print((wave[x], smoothed[0][x]))
        #print((wave[x],))
        #print((fft[0][x],))
        #time.sleep(0.05)

    #for x in range(len(convoluted)):
        #print((convoluted[x],))
        #time.sleep(0.01)

    #fft = ulab.numerical.flip(fft)

    #print(len(fft))
    #time.sleep(3)
    #print((fft,))
    #time.sleep(5)
    #freq_res = (1/time_step)/power
    #print(get_freq(smoothed[0]) * 4)
    #print("frequency is ", float(ulab.numerical.argmax(fft[round((70*time_step)*power):round((440*time_step)*power)])/power) * (1/time_step))
    #print("frequency is ", float(ulab.numerical.argmax(fft)/power) * (1/time_step), '\n')
    #if ulab.numerical.max(a[round(70/freq_res):round(440/freq_res)]) < 15000:
        #print('No frequency detected\n')
    #else:
        #print("frequency is ", (ulab.numerical.argmax(a[round(71/freq_res):round(381/freq_res)]) + round(71/freq_res)) * freq_res, '\n')
    #print('DB is: ', ulab.numerical.max(a[round(70/freq_res):round(440/freq_res)]), '\n')
    #print("frequency is ", (ulab.numerical.argmax(a[100:1000]) + 100) * freq_res, '\n')

    #motorPos = set_motor_pos(dial_right_pos, motorPos)
    motorPos = display_freq(freq, motorPos)

    #time.sleep(5)
    #flag = False