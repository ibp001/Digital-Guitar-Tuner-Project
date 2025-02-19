# ECEG201_S2021
Github for ECEG 201 for Spring 2021

Full DAMNED Code.py is the original application code that can be modified for custom applications

Tuner.py is the finished code for my application and is the main code to run

README.md  This file

espFunctions.py  Functions needed for wifi connectivity

motorFunctions.py  Functions to operate the motor

neopixelFunctions.py  Various functions to display data on the neopixel ring

neopixelFunctionsEXAMPLES.py  Some examples of how to use the functions

secrets.py  The file that contains login information for Bucknell's network.  YOu need to modify this if you are using it on another network.






Inputs:

- Electric Guitar
  - Guitar -> guitar amplifier -> 3.5mm audio jack adapter -> pinout to feather analogIO
  - This setup produced the most reliable and consistent signal and made it easy to manipulate and dial in the signal to a usable form
- A kill switch
  - Uses a potentiometer (since that's all I have on me) as a kill switch for the program
  - When the kill switch is used, the full time it took to tune the guitar is calculated and the program ends

Outputs:

- Pitch Meter
  - On the top, displays via a meter how sharp or flat a detected note is from the target note
  - On the bottom, displays the assumed target note by lighting up one of six LEDs green corresponding to the six open-string notes of a guitar in standard EADGBE tuning.
- Thingspeak channel
  - Field 1 contains detected frequency data
  - Field 2 contains the total time it took to tune the guitar






Where there is room for improvement:

The only thing that did not work quite as much as I wanted was the frequency/pitch detection algorithm. This was by far the biggest challenge I faced with this project, and I tried multiple different methods of achieving this.

First I tried to simply detect and count either the number of peaks, zeros, or valleys in the raw waveform, which worked terribly since there was so much noise in the signal, as well as the interference of the natural harmonics of the strings.

Second, after a bit of research, I discovered Adafruit’s built in data processing “api” for CircuitPython called ulab (pronounced “microlab”) that had a myriad of functions that could potentially be useful for what I was doing. ulab is able to perform heavy calculations over large arrays of data much faster than normal python, which would save a lot of computation time between each waveform sampling and output display. I first tried to use its Fast Fourier Transform function in order to get the set of frequencies that was making up the audio signal, and I expected the fundamental frequency of whatever note I was playing to be the loudest and most prominent frequency. Unfortunately, not only did this not work with the lower notes as sometimes the harmonics would be more prominent than the actual note itself, but those ulab functions had very poor documentation that I believe was also outdated because the ulab functions I had available in my installed version did not match what was listed in the documentation. Because of these issues, I wasn’t able to figure out how to properly use and implement the functions for what I was trying to do.

Finally, after a lot more research, I turned to autocorrelation as my last option. This method ended up being much more viable and easier to implement, and I used another function available from the ulab library; convolution. At first I had a little bit of trouble getting it to work because of the poor documentation, but after a lot of tinkering I was able to configure it in a way to give me an autocorrelation function that produced a much smoother signal wave that I was then able to use in my initial peak detection algorithm to find the period of the original signal, and therefore the frequency. 

While this method worked the best and was more reliable and consistent than any of the other methods I tried, it still had some issues with it, such as higher frequency signals dying down below detection levels very fast, or how sometimes the detected frequency would bounce back and forth between two different values on lower frequency signals. These issues could be caused by my peak detection algorithm or by some weird issue with the convolution function that I’m not seeing. Overall, this method at least produced a usable frequency detection result that I was able to make work for the final application, but it could still be heavily improved upon and made much more reliable and consistent.
