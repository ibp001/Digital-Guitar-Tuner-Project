import time
import board
import neopixel
from neopixelFunctions import *


NUM_LEDS = len(get_ring())



#----------Examples-------------

print("ring color and brightness setting")
ring_color((255,0,255))
time.sleep(1)
set_brightness(1)
time.sleep(1)
set_brightness(.1)
print("")

print("bar graph fill mode")
bar_graph((255,0,0),10)
time.sleep(2)
print("")

print("bar graph dot mode")
bar_graph((0,255,0),10, False)
time.sleep(2)
print("")

print("bar graph fill from 1 - 10")
bar_graph((255,0,0), 10, start_pos = 1)
time.sleep(2)
print("")

print("bar graph fill from 5 - 15")
bar_graph((0,255,0), 15, start_pos = 5)
time.sleep(2)
print("")


print("shaded bar graph from red to blue")
shaded_bar_graph((255,0,0), (0,0,255), 24)
time.sleep(2)
print("")

print("shaded bar graph from blue to red from led 10 to 24")
shaded_bar_graph((0,0,255), (255,0,0), 24, start_pos = 10)
time.sleep(2)
print("")


print("Error handling")
print("Should say that the end pos is too large")
bar_graph((0,0,0), 100)
time.sleep(1)
print("")

print("Should say that the color is invalid")
bar_graph((0,0),10)
bar_graph((0,700,0),10)
bar_graph((0,-100,0),10)
time.sleep(2)
print("")


print("snake =D")
animate_snake()