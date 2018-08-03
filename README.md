# Bandotuner
An opensource tool to measure and tune bandoneons (and accordions).

# Requirements

- pandas
- numpy
- numpy-ringbuffer
- scipy
- bokeh
- pyaudio

# Run
bokeh serve streamer.py

go to: http://localhost:5006/streamer

![dashboard](https://user-images.githubusercontent.com/10183650/43246021-a4abf52a-90b0-11e8-8bad-53e54ac2bfad.png)


# Build Pyinstaller
I had to remove the pyqt4 hook from "C:\Anaconda3\Lib\site-packages\PyInstaller\loader\rthooks.dat"

'''
pyinstaller --hidden-import=scipy._lib.messagestream --hidden-import=pandas._libs.tslibs.np_datetime --hidden-import=pandas._libs.tslibs.nattype --hidden-import=pandas._libs.tslibs.timedeltas --hidden-import=pandas._libs.skiplist start_bandotuner.py
'''