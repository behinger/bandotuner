#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 10:15:42 2018

@author: behinger
"""


import numpy as np
import pyaudio
from collections import deque
from scipy.fftpack import fft
from numpy_ringbuffer import RingBuffer
from scipy.signal.windows import hann

# Object to get the audiostream + do the FFT
class AudioStream(object):
    def __init__(self,rate=8192):
        # stream constants
        self.RATE = rate
        self.CHUNK = int(self.RATE/10) # 4 times per second
        self.FORMAT = pyaudio.paFloat32
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
        # at first I wanted to extend the data previously recorded, but obviously they were recorded at a different sampling rate. We therefore have to start anew
        self.buffsize =int(self.RATE*self.T)
        #self.buff = deque(maxlen=self.buffsize)
        self.buff = RingBuffer(capacity=self.buffsize,dtype=np.int16)
        self.fftwindow = hann(self.buffsize)
    def fill_buffer(self, in_data, frame_count, time_info, status_flags):
            """Continuously collect data from the audio stream, into the buffer."""
            d_converted = np.fromstring(in_data, 'int16')
            #print(d_converted)
            self.buff.extend(d_converted)
            #self.buff.extend(in_data[1::2])
            return None, pyaudio.paContinue
        
    def calc_fft(self):
        data = np.array(self.buff)
        if data.shape[0]!= self.buffsize:
            print('no sample')
            return(None)
        data = np.multiply(data,self.fftwindow)
        yf = fft(data)
        yf = yf[1:int(yf.shape[0]/2)]
        fftdata =   np.abs(yf)
        
        return(fftdata)

