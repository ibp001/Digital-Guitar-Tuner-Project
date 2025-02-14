# define the function wheel which is adapted from the CircuitPython
# tutorial pages:
# https://learn.adafruit.com/circuitpython-essentials/circuitpython-internal-rgb-led
# Note that the neopixel needs three colors: red, green, and blue
# You write a value from 0 = off to 255 = full on to each color to set the
# overall brightness and color.  For example 255,0,0 is bright red.
# 0, 128, 0 is medium green and 0, 128, 128 would be cyan (equal green and blue).
# White is when the red, green, and blue numbers are equal.
def wheel(pos):
    # Input a value between 0 to 255 to get a color value.
    # Expects an input between 0 to 255 but will cap off if outside that range.
    # The colours are a transition b - g - r.
    if pos <= 0: #If out of range below 0, cap at 0 and return blue.
        return 0, 0, 255
    elif pos < 127:  # If low value, light green and blue.
        return 0, int(pos * 2), int(255 - (pos * 2))
    elif pos < 255:  # If high value, light red and green.
        return int(2*(pos - 127)), int(255 - 2*(pos - 127)), 0
    else :   # If out of range above 255, cap at 255 and return red.
        return 255, 0, 0

def setpoint(temp, temp_range, center):
    # Scales a temperature to value from 0 to 255.
    # temp is temperature value in Celcius.
    # range is scaling range.  If range = 10 then center-10 returns
    # 0 and center+10 returns 255.
    # center is the offset of the input value.  If center = 25 then
    # temp = 25 returns 127, the center of the range.
    x = int(((temp - center)/(2*temp_range))*(256) + 127)
    if x <= 0:      # This is just to make sure we don't exceed the
        return 0    # specified range and produce an error.
    elif x >= 255:
        return 255
    else:
        return x

def heatindex(T, R):
    # This function is taken from the heat index Wikipedia page.
    # It's set to return a blinkrate based on the
    # various zones defined in that article.
    c1 = -8.78469475556
    c2 = 1.61139411
    c3 = 2.33854883889
    c4 = -0.14611605
    c5 = -0.012308094
    c6 = -0.0164248277778
    c7 = 0.002211732
    c8 = 0.00072546
    c9 = -0.000003582
    # Above we defined the constants by just copying them from the Wikipedia
    # article.  Below HI is the heat index formula from that article translated
    # into Python math.
    HI = c1 + c2*T + c3*R + c4*T*R + c5*(T**2) + c6*(R**2) + c7*(T**2)*R + c8*T*(R**2) + c9*(T**2)*(R**2)

    if HI > 54:
        return 0.1
    elif HI > 41:
        return 0.25
    elif HI > 32:
        return 0.5
    elif HI > 26:
        return 1
    else:
        return 0