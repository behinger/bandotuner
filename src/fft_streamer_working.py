#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 16:50:47 2018

@author: behinger
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 10:54:26 2018

@author: behinger
"""

import matplotlib.pyplot as plt
import numpy as np
import pyaudio
#from pyqtgraph.Qt import QtGui, QtCore
#import pyqtgraph as pg
import struct
from scipy.fftpack import fft
from scipy.signal import decimate
import sys
import time
from collections import deque

import pandas as pd
import numpy as np
np.random.seed(1)

from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, Slider, Select
from bokeh.plotting import curdoc, figure
from bokeh.driving import count
from bokeh.plotting import figure, output_file, show

source = ColumnDataSource(dict(
    freq=[0,1], fft=[0,2]))


p = figure(plot_height=500, tools="xpan,xwheel_zoom,xbox_zoom,reset" )
#p2 = figure(plot_height=500, tools="xpan,xwheel_zoom,xbox_zoom,reset")

p.x_range.range_padding = 0

p.line(x='freq', y='fft', line_width=3, color='navy', source=source)
#p2.line(x='time', y='fft', line_width=3, color='navy', source=source)



class AudioStream(object):
    def __init__(self):
        
        # stream constants
        self.RATE = 2*4096
        self.CHUNK = int(self.RATE/10) # 4 times per second
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        
        self.pause = False
        self.T =4 # 
        self.init_buff()
        # stream object
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1, rate=self.RATE,
            input=True, frames_per_buffer=self.CHUNK,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self.fill_buffer,
)
    def init_buff(self):
        self.buffsize =int(self.RATE*self.T)
        tmp = None
        if hasattr(self,'buff'):
            tmp = self.buff
        self.buff = deque(maxlen=self.buffsize) # resolution of 1/4 Hz should be plenty
        if tmp:
            self.buff.extend(tmp)
    def fill_buffer(self, in_data, frame_count, time_info, status_flags):
            """Continuously collect data from the audio stream, into the buffer."""
            self.buff.extend(in_data[1::2])
            return None, pyaudio.paContinue
        
    def calc_fft(self):
        data = np.array(self.buff)
        if data.shape[0]==0:
            print('no sample')
            return(None)
        
        yf = fft(data)
        yf = yf[1:int(yf.shape[0]/2)]
        fftdata =   np.abs(yf)
        
        return(fftdata)

  

streamer = AudioStream()

def update():
        data = streamer.calc_fft()
        freqs = np.array(range(data.shape[0])) / streamer.T
        ix = freqs>100
        freqs = freqs[ix]
        data  = data[ix]
        if type(data) != type(None):
            new_data = dict(
                    freq=freqs.tolist(),
                    fft = data.tolist(),
            )
            source.stream(new_data, data.shape[0])

def changeT(attr,old,new):
    streamer.T = 1/new
    streamer.init_buff() # reinit the buffer
    
length_slider = Slider(value=1/streamer.T,start=0.1, end=5, step=.1,
                    title="Frequency Resolution (high resolution => long time integration) [Hz]")
length_slider.on_change('value',changeT)



curdoc().add_root(column(p,length_slider))

curdoc().add_periodic_callback(update, 100)
curdoc().title = "FFT"