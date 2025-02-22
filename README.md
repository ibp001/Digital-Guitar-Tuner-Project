# ECEG201_S2021
Github for ECEG 201 for Spring 2021

---

## Files

**Full DAMNED Code.py**  -  The original application code that can be modified for custom applications

**Tuner.py**  -  The finished code for my application and the main code to run (would be renamed "code.py" when uploaded onto feather m4)

**README.md**  -  This file

**espFunctions.py**  -  Functions needed for wifi connectivity

**motorFunctions.py**  -  Functions to operate the motor

**neopixelFunctions.py**  -  Various functions to display data on the neopixel ring

**neopixelFunctionsEXAMPLES.py**  -  Some examples of how to use the functions

**secrets.py**  -  The file that contains login information for Bucknell's network.  You need to modify this if you are using it on another network

**Guitar Tuner Datasheet.pdf**  -  the datasheet which contains all technical information about this divice and my application of it

---

## Inputs:

- Electric Guitar
  - Guitar -> guitar amplifier -> 3.5mm audio jack adapter -> pinout to feather analogIO
  - This setup produced the most reliable and consistent signal and made it easy to manipulate and dial in the signal to a usable form
- A kill switch
  - Uses a potentiometer (since that's all I have on me) as a kill switch for the program
  - When the kill switch is used, the full time it took to tune the guitar is calculated and the program ends

## Outputs:

- Pitch Meter
  - On the top, displays via a meter how sharp or flat a detected note is from the target note
  - On the bottom, displays the assumed target note by lighting up one of six LEDs green corresponding to the six open-string notes of a guitar in standard EADGBE tuning.
- Thingspeak channel
  - Field 1 contains detected frequency data
  - Field 2 contains the total time it took to tune the guitar

---

## Demo Video:

<a href="https://www.youtube.com/watch?v=b3vKT6Wksjo&ab_channel=IsidorePhilosophe" target="_blank"><img src="https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/315f97193fbd75498d2cc2093bd8aeafb589b0c4/Build%20Photos/Demonstration%20Video%20Thumbnail.png" alt="Click here for youtube link" width="240" height="180" border="10" /></a>

[Click Here for youtube link](https://www.youtube.com/watch?v=b3vKT6Wksjo&ab_channel=IsidorePhilosophe)

---

## Where there is room for improvement:

The only thing that did not work quite as much as I wanted was the frequency/pitch detection algorithm. This was by far the biggest challenge I faced with this project, and I tried multiple different methods of achieving this.

First I tried to simply detect and count either the number of peaks, zeros, or valleys in the raw waveform, which worked terribly since there was so much noise in the signal, as well as the interference of the natural harmonics of the strings.

Second, after a bit of research, I discovered Adafruit’s built in data processing “api” for CircuitPython called ulab (pronounced “microlab”) that had a myriad of functions that could potentially be useful for what I was doing. ulab is able to perform heavy calculations over large arrays of data much faster than normal python, which would save a lot of computation time between each waveform sampling and output display. I first tried to use its Fast Fourier Transform function in order to get the set of frequencies that was making up the audio signal, and I expected the fundamental frequency of whatever note I was playing to be the loudest and most prominent frequency. Unfortunately, not only did this not work with the lower notes as sometimes the harmonics would be more prominent than the actual note itself, but those ulab functions had very poor documentation that I believe was also outdated because the ulab functions I had available in my installed version did not match what was listed in the documentation. Because of these issues, I wasn’t able to figure out how to properly use and implement the functions for what I was trying to do.

Finally, after a lot more research, I turned to autocorrelation as my last option. This method ended up being much more viable and easier to implement, and I used another function available from the ulab library; convolution. At first I had a little bit of trouble getting it to work because of the poor documentation, but after a lot of tinkering I was able to configure it in a way to give me an autocorrelation function that produced a much smoother signal wave that I was then able to use in my initial peak detection algorithm to find the period of the original signal, and therefore the frequency. 

While this method worked the best and was more reliable and consistent than any of the other methods I tried, it still had some issues with it, such as higher frequency signals dying down below detection levels very fast, or how sometimes the detected frequency would bounce back and forth between two different values on lower frequency signals. These issues could be caused by my peak detection algorithm or by some weird issue with the convolution function that I’m not seeing. Overall, this method at least produced a usable frequency detection result that I was able to make work for the final application, but it could still be heavily improved upon and made much more reliable and consistent.

---

## Build Photos:

Attaching surface mounted components with solder paste, a stencil, and a reflow oven:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%201.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 1.jpg")

Attaching throughhole components manually with soldering iron, solder wire, and flux:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%202.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 2.jpg")

Assembling Adafruit Feather M4 Express microcontroller onto board using the female pin headers added last step:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%203.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 3.jpg")

3D printing the enclosure and dial arm with PLA filament:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%204.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 4.jpg")

Lasercutting the mounting plates out of plywood and attaching stepper motor to the main plate:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%205.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 5.jpg")

Soldering leads onto the Neopixel ring of 24 individually addressable RGB LEDs:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%206.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 6.jpg")

Attaching the Neopixel ring onto the main mounting plate:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%207.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 7.jpg")

Lasercutting an acrylic diffuser for the Neopixel LEDs and assembling the main display:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%208.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 8.jpg")

Assembling the display and pcb together:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%209.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 9.jpg")

Soldering the Neopixel ring and wiring the motor into pcb to connect main display:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%2010.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 10.jpg")

Attaching front piece of enclosure:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%2011.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 11.jpg")

Display with enclosure:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%2012.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 12.jpg")

Final assembly with full enclosure and attached dial arm and stopper:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%2013.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 13.jpg")

Full demonstration setup:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%2014.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 14.jpg")

Closeup of device running and showing display:
![alt text](https://github.com/ibp001/Digital-Guitar-Tuner-Project/blob/1f31ce5507239ff1a26a97d3e6b5bab9dc77757a/Build%20Photos/ECEG%20201%20-%20D.A.M.N.E.D%20Project%20Guitar%20Tuner%2015.jpg "ECEG 201 - D.A.M.N.E.D Project Guitar Tuner 15.jpg")

[Watch the demonstration video here](https://www.youtube.com/watch?v=b3vKT6Wksjo&ab_channel=IsidorePhilosophe)
