#   ECEG 201 Final Application Project
#   Author: Izzy Philosophe
#   Application: Guitar Tuner
#
#   Inputs:
#       - Electric Guitar
#           - Guitar -> guitar amplifier -> 3.5mm audio jack adapter -> pinout to feather analogIO
#           - This setup produced the most reliable and consistent signal and made it easy to
#             manipulate and dial in the signal to a usable form
#       - A kill switch
#           - Uses a potentiometer (since thats all I have on me) as a kill switch for the program
#           - When the kill switch is used, the full time it took to tune the guitar is calculated
#             and the program ends
#       - Adafruit ulab API for CircuitPython, for signal data processing
#           - ulab is able to perform heavy calculations over large arrays of data much faster than
#             normal python.
#           - This saves a lot of computation time between each waveform sampling and output display
#
#   Outputs:
#       - Pitch Meter
#           - On the top, displays via a meter how sharp or flat a detected note is from the target
#             note
#           - On the bottom, displays the assumed target note by lighting up one of six LEDs green
#             corresponding to the six open-string notes of a guitar in standard EADGBE tuning.
#       - Thingspeak channel
#           - Field 1 contains detected frequency data
#           - Field 2 contains the total time it took to tune the guitar




#---------------------- Library Imports ---------------------------

import time
import board
from analogio import AnalogIn
import math
import neopixelFunctions
import espFunctions
import motorFunctions
import ulab





#-------------------- Functions ---------------------------


# returns the value of the analog pin in volts
def get_voltage(pin):
    return (pin.value * 3.3) / 65536


# centers the inputted waveform to revolve around 0
def center(array):
    avg = float(sum(array) / len(array))
    for x in range(len(array)):
        array[x] = (array[x] - avg)
    return array


# This function is the pitch detection algorithm.
# It uses ulab to implement an autocorrelation technique for finding the period of the waveform via
#   convolution.
# It takes a small portion of the waveform sample and convolves it against the entire waveform to
#   plot out the overlap of the signals over the timeshift/lag, then measures the distance between
#   two peaks of the result, giving the period of the original signal.
# Since the convolution function reverses the second input wave (as is normal for convolution),
#   the small portion is flipped first to negate this.
def get_freq_correlation(wave, time_delta):
    length = len(wave)
    # Controlls the size of the signal cutout, in number of samples.
    sample_size = 512
    # Controlls the threshold at which the function registers a peak relative to the max value of
    #   the correlation wave.
    threshold = 0.91

    # Computes the correlation through ulab functions.
    uwave = ulab.array(wave)
    correlation = ulab.filter.convolve(uwave, ulab.numerical.flip(uwave[0:sample_size]))
    match = ulab.numerical.max(correlation)
    match_location = ulab.numerical.argmax(correlation)

    local_max = []
    local_max.clear()
    count = 0

    # Starting at the absolute max of the correlation wave, it goes through the array until it
    #   leaves the first peak.
    while correlation[match_location + count] >= (match * threshold):
        count += 1
        if (match_location + count) == len(correlation):
            return 0.0

    # It then waits until it registers another peak, depending on the set threshold of the
    #   absolute max value
    while correlation[match_location + count] < (match * threshold):
        count += 1
        if (match_location + count) == len(correlation):
            return 0.0
    start = count

    # once a new peak is registered, it records the whole peak into a new array and stops when it
    #   leaves the peak threshold
    while correlation[match_location + count] >= (match * threshold):
        local_max.append(correlation[match_location + count])
        count += 1
        if (match_location + count) == len(correlation):
            return 0.0

    # finds the exact location of the second peak
    second_peak = ulab.numerical.argmax(local_max)
    # calculates the period of the signal
    period = float((second_peak + start) * time_delta)
    # calculates and returns the frequency
    frequency = float(1/period)
    if period == 0:
        frequency = 0.0
    return frequency


# This is the function for displaying the detected frequency on the pitch meter.
# The function first finds which note the frequency is closest to based on a predefined list of
#   reference points.
# It then calculates how many half-steps (or semitones in the UK) either sharp or flat the
#   frequency is compared to the target note.
# The meter then displays how sharp or flat the detected note is with a boundary of 2.5 half-steps
#   to either side.
# The relationship between the frequency and the percieved pitch is not linear, but instead
#   logarithmic, so it calculates the half-steps using a logarithmic function based on the current
#   tuning standard of 12 Tone Equal Temperament, which divides each octave equally into 12 half-steps.
def display_freq(frequency):

    if (frequency >= 71.326) and (frequency < E2_A2_midpoint):

        neopixelFunctions.bar_graph((255, 255, 255), 22, True, 16, ring, False)
        neopixelFunctions.set_pixel((0, 255, 0), 21)

        myMotor.set_position_degrees(dial_center_pos +(meter_bounds*((12/2.5)*math.log(freq/E2, 2))))

    elif (frequency >= E2_A2_midpoint) and (frequency < A2_D3_midpoint):

        neopixelFunctions.bar_graph((255, 255, 255), 22, True, 16, ring, False)
        neopixelFunctions.set_pixel((0, 255, 0), 20)

        myMotor.set_position_degrees(dial_center_pos +(meter_bounds*((12/2.5)*math.log(freq/A2, 2))))

    elif (frequency >= A2_D3_midpoint) and (frequency < D3_G3_midpoint):

        neopixelFunctions.bar_graph((255, 255, 255), 22, True, 16, ring, False)
        neopixelFunctions.set_pixel((0, 255, 0), 19)

        myMotor.set_position_degrees(dial_center_pos +(meter_bounds*((12/2.5)*math.log(freq/D3, 2))))

    elif (frequency >= D3_G3_midpoint) and (frequency < G3_B3_midpoint):

        neopixelFunctions.bar_graph((255, 255, 255), 22, True, 16, ring, False)
        neopixelFunctions.set_pixel((0, 255, 0), 18)

        myMotor.set_position_degrees(dial_center_pos +(meter_bounds*((12/2.5)*math.log(freq/G3, 2))))

    elif (frequency >= G3_B3_midpoint) and (frequency < B3_E4_midpoint):

        neopixelFunctions.bar_graph((255, 255, 255), 22, True, 16, ring, False)
        neopixelFunctions.set_pixel((0, 255, 0), 17)

        myMotor.set_position_degrees(dial_center_pos +(meter_bounds*((12/2.5)*math.log(freq/B3, 2))))

    elif (frequency >= B3_E4_midpoint) and (frequency < 380.836):

        neopixelFunctions.bar_graph((255, 255, 255), 22, True, 16, ring, False)
        neopixelFunctions.set_pixel((0, 255, 0), 16)

        myMotor.set_position_degrees(dial_center_pos +(meter_bounds*((12/2.5)*math.log(freq/E4, 2))))

    else:
        neopixelFunctions.bar_graph((255, 255, 255), 22, True, 16, ring, False)
    return





#------------------ Initializations and Setup ----------------------


# Sets up the audio signal input
kill_switch = AnalogIn(board.A0)
audio_in = AnalogIn(board.A1)



# Sets up the motor and defines the centerpoint and boundaries for the pitch meter
myMotor = motorFunctions.ECEGMotor(False)

dial_center_pos = 151
meter_bounds = 61



# Designated open-string notes and their frequencies (Hz):
E2 = 82.407

E2_A2_midpoint = 95.209

A2 = 110.000

A2_D3_midpoint = 127.089

D3 = 146.832

D3_G3_midpoint = 169.643

G3 = 195.998

G3_B3_midpoint = 220.000

B3 = 246.942

B3_E4_midpoint = 285.305

E4 = 329.628


# Sets up the esp and connects to the thingspeak channel
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

ssid = "[Insert network ssid here]"
password = "[Insert network password here]"
channel_ID = 0000000 #[Insert 7-digit thingspeak channel ID here]
thingspeak_api_key = '[Insert thingspeak api key here]'

tool_time = espFunctions.ESP_Tools(secrets['ssid'], secrets['password'], secrets['channel_ID'], secrets['api_key'])
print("Done!")


# initiallizing the LEDS
ring = neopixelFunctions.get_ring()
neopixelFunctions.bar_graph((255, 0, 0), 11, True, 3, ring, False)
neopixelFunctions.bar_graph((255, 100, 0), 10, True, 4, ring, False)
neopixelFunctions.bar_graph((255, 255, 0), 9, True, 5, ring, False)
neopixelFunctions.bar_graph((0, 255, 0), 8, True, 6, ring, False)
# The bottom LEDS will be lit red while the program waits for the kill switch to be reset
neopixelFunctions.bar_graph((255, 0, 0), 22, True, 16, ring, False)


# centers the dial on the pitch meter
myMotor.set_position_degrees(dial_center_pos)

# waits for the kill_switch to be turned off before starting the program
while get_voltage(kill_switch) > 0.5:
    print("Reset the kill switch to start")
    time.sleep(1)
# bottom LED bar turns white when kill switch is reset
neopixelFunctions.bar_graph((255, 255, 255), 22, True, 16, ring, False)




#------------------------------- Main Loop --------------------------------------


count = 0
loop = True
tuning_start_time = time.monotonic()
while loop:

    # samples the audio voltage signal for about 164 ms and stores it all in a list
    power = 2048
    wave = []
    wave.clear()

    start_time = time.monotonic_ns()
    for x in range(power):
        wave.append(get_voltage(audio_in))
    end_time = time.monotonic_ns()

    # calculates the total time of the sample and the time step between each sample instance
    total_time = float((end_time - start_time)/1000000000)
    time_step = float(total_time/power)

    # calculates and displays the frequency of the signal sample
    freq = get_freq_correlation(center(wave), time_step)
    print('frequency: ', freq, 'Hz\n')
    display_freq(freq)
    count += 1

    # Pushes the current detected frequency to the thingspeak channel.
    # It's limited to only push every 20 samples because it adds a lot of execution time.
    if count == 20:
        tool_time.push_to_field(1, freq)
        print('')
        count = 0

    # If the kill switch is turned all the way up, it measures the total time it took to tune the
    #   guitar (in seconds), then pushes this time to the thingspeak server, sets the bottom LED
    #   bar to all green, and stops the program.
    if get_voltage(kill_switch) > 2.0:
        total_tuning_time = time.monotonic() - tuning_start_time
        print("total tuning time: ", total_tuning_time, 'seconds\n')
        tool_time.push_to_field(2, total_tuning_time)
        print('')
        neopixelFunctions.bar_graph((0, 255, 0), 22, True, 16, ring, False)
        loop = False