# This repository includes the program files for my Capstone Project on Biomusic. 

## Flow diagram:
<br>
![alt tag](https://github.com/souzanmirza/Biomusic/blob/master/flowdiagram.jpg)

## Description:
Biomusic translates the digitized physiological signal data, namely ECG, GSR and skin temperature into real time changes (pitch, tempo, volume) to music tracks.

This program is implemented in Python using a threaded producer-consumer paradigm. The consumer constantly polls for serial data from the Arduino and passes it to the threads which handle the processing and extraction of signal deviations from the physiological data which then pipes the deviations to a set of consumers which maps and applies the changes to the music tracks in realtime.

## Requirements:
<ul>
	<li><a href="https://pypi.python.org/pypi/pyserial">Pyserial</a></li>
	<li><a href="https://github.com/bokeh/bokeh">Bokeh</a></li>
	<li><a href="https://pypi.python.org/pypi/pywin32">pywin32</a></li>
	<li><a href="https://pypi.python.org/pypi/comtypes">comtypes</a></li>
	<li><a href="https://github.com/librosa/librosa">librosa</a></li>
	<li><a href="https://people.csail.mit.edu/hubert/pyaudio/">PyAudio</a></li>
	<li>Matplotlib</li>
	<li>NumPy</li>
	<li>SciPy</li>
</ul>

## Execution:
With a valid serial input with 3 ADC ports run the serial-gsr-ecg-temp.py.

