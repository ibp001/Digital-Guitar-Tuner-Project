# Bucknell University
# ECEG 201
# Spring 2021
# Instructors:  Alan Cheville, Matt Lamparter

import time
import rtc
import board
import busio
from digitalio import DigitalInOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import neopixel
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import module3_funcs # created by Alan Cheville for Module 3 of this course

# test out the RTC feature of the Feahter M4
clock = rtc.RTC()
# manually set the date and atime
clock.datetime=(2021,2,10,12,37,0,3,41,1)
print(clock.datetime.tm_year)
time.sleep(3)
print(clock.datetime)


# Choose "home" or "Bucknell"
location = "Bucknell"

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

# the offset value for temperature.  If temperature = offset then the LED will be green
# corresponding to the center of the range
offset = 22
# the range of degrees C for full color display.  Blue will
# be setpoint - range for the lower bound and red will be setpoint + range
# for the upper bound.
range = 10
#Define the condition where the neopixel
# is off.  Note that the neopixel expects integer numbers
off = int(0), int(0), int(0)

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

# begin the main loop of the device, checking for temp/humidity and then updating arm and NeoPixels
while True:
    # get Maker-E temperature
    print(clock.datetime)
    currentTemp = requests.get(TEXT2_URL)
    x = float(currentTemp.text)
    x = (x-32)/1.8 # convert F to C
    currentTemp.close()
    print("Maker-E outside temperature right now is ", x, "°C.")
    time.sleep(1)
    # get Maker-E relative humidity
    currentRH = requests.get(TEXT2_URL2)
    y = float(currentRH.text)
    currentRH.close()
    print("Maker-E outside RH right now is ", y, "%.")
    time.sleep(1)

    # define an updated motor arm position based on RH
    newMotorPos = int(y/100 * maxMotor)
    # see if there is a change in motor arm position
    delta = newMotorPos - motorPos
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
    motorPos = newMotorPos

    i = module3_funcs.setpoint(x, range, offset)  # scale the temperature to a value
    # from 0 to 255 using the setpoint function.
    blinkrate = module3_funcs.heatindex(int(x), int(y))
    # get the blink rate which depends on what the heat index is.  The more
    # dangerous the heat index the faster the blink rate.  No danger sets
    # blinkrate to zero

    if blinkrate == 0:
        pixel.fill(module3_funcs.wheel(i))  # turn on the led with the color
        pixel.show()
        time.sleep(1)   # corresponding to the temperature using the wheel function
        print("blinkrate = 0 and i=",i," and module3 output=",module3_funcs.wheel(i))
    # this does not blink the light.
    if blinkrate > 0:
        # the wheel() function was throwing an error when i = 255 so it is necessary to ensure i never reaches 255
        pixel.fill(module3_funcs.wheel(i-1))  # light the LED
        pixel.show()
        time.sleep(blinkrate)
        #pixel.fill(off)    # turn off the LED
        #pixel.show()
        #time.sleep(blinkrate)
        print("blinkrate != 0 and i=",i," and module3 output=",module3_funcs.wheel(i-1))
    # update the display once every minute
    time.sleep(60)
