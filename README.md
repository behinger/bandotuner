# Bandotuner
An opensource tool to measure and tune bandoneons (and accordions).

# Requirements

- pandas
- numpy>=1.13
- numpy-ringbuffer
- scipy
- bokeh
- sounddevice
- peakutils 

# Run
bokeh serve streamer_v2.py


go to: http://localhost:5006/streamer

![dashboard](https://user-images.githubusercontent.com/10183650/43246021-a4abf52a-90b0-11e8-8bad-53e54ac2bfad.png)


# Build Pyinstaller
Currently I need to put the libportaudio32bit.dll (or 64bit) in the folder 
Also the download.js to download the table needs to be bundled. I added everything to the start_bandotuner.spec

To binarize:
pyinstaller start_bandotuner.spec


This I used to initialize the start_bandotuner.spec file
```
pyinstaller start_bandotuner.py --hidden-import sounddevice --log-level=DEBUG -y --add-binary libportaudio32bit.dll;_sounddevice_data/portaudio-binaries/.
```
