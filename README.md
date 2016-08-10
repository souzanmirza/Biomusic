This repository includes the program files for my Capstone Project on Biomusic. 

Biomusic translates the digitized physiological signal data, namely ECG, GSR and skin temperature into real time changes (pitch, tempo, volume) to music tracks.

This program is implemented in Python using a threaded producer-consumer paradigm. The consumer constantly polls for serial data from the Arduino and passes it to the threads which handle the processing and extraction of signal deviations from the physiological data which then pipes the deviations to a set of consumers which maps and applies the changes to the music tracks in realtime.
