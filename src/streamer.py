#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 10:54:26 2018

@author: behinger
"""

import matplotlib.pyplot as plt
import numpy as np

import audiostream
import pandas as pd
import numpy as np

np.random.seed(1)

from bokeh.layouts import row, column, gridplot,widgetbox
from bokeh.models import ColumnDataSource, Slider, Select, Button,LabelSet

from bokeh.plotting import curdoc, figure,output_file, show
from bokeh.driving import count

import hz_to_scale
import peakutils

source = ColumnDataSource(dict(freq=[], fft=[]))
source_signal = ColumnDataSource(dict(time=[],signal=[]))

sourcepeak = ColumnDataSource(dict(freq=[],fft=[]))

# we add index here to easily provide a pandas dataframe later
source_f1= ColumnDataSource(dict(freq=[],fft=[],index=[]))

source_f2= ColumnDataSource(dict(freq=[],fft=[],index=[]))

source_line_f1 =ColumnDataSource(dict(freq=[],fft=[],index=[],color=[],label=[]))
source_line_f2 =ColumnDataSource(dict(freq=[],fft=[],index=[],color=[],label=[]))


p_time = figure(plot_height=150, tools="xpan,xwheel_zoom,xbox_zoom,reset" )
p_time.line(x='time', y='signal', line_width=3, color='navy', source=source_signal)
# main FFT figure
p = figure(plot_height=300, tools="xpan,xwheel_zoom,xbox_zoom,reset" )

# We add the fft power spectra
p.line(x='freq', y='fft', line_width=3, color='navy', source=source)
# After we identified peaks (to detect the fundamental), we add the peaks in here
p.circle(x='freq',y='fft',color='red',source=sourcepeak)

# This plot is a zoomed in version of the fundamental
p_f1 = figure(plot_height=500, tools="xpan,xwheel_zoom,xbox_zoom,reset" )
p_f1.line(  x='freq', y='fft', line_width=3, color='navy', source=source_f1)
p_f1.circle(x="freq", y='fft', color='color',source=source_line_f1,size=7)

# this plot is a zoomed in version of 2x the fundamental
p_f2 = figure(plot_height=500, tools="xpan,xwheel_zoom,xbox_zoom,reset" )
p_f2.line(  x='freq', y='fft', line_width=3, color='navy', source=source_f2)
p_f2.circle(x="freq", y='fft', color='color',source=source_line_f2,size=7)


p_f1.add_layout(LabelSet(x='freq', y='fft', text='label', level='glyph',
              x_offset=5, y_offset=5, source=source_line_f1, render_mode='canvas'))
p_f2.add_layout(LabelSet(x='freq', y='fft', text='label', level='glyph',
              x_offset=5, y_offset=5, source=source_line_f2, render_mode='canvas'))

#%%
# This is the main streamer
streamer = audiostream.AudioStream()
converter = hz_to_scale.hz_to_scale(436)
#%%
# Update the top plot (the fundamental zoom is button triggered atm)
def update():
        # get the FFT
        data = streamer.calc_fft()
        
        # at what frequencies are the FFTs? 
        # TODO: possible bug here -frequencies shifted by 1?
        freqs = (np.array(range(data.shape[0]))+1) / streamer.T

        # Let's remove frequencies lower than 100
        # TODO: Make this a slider
        ix = freqs>100
        freqs = freqs[ix]
        data  = data[ix]

        # If data remains, add it to the power spectra
        if type(data) != type(None):
            new_data = dict(
                    freq = freqs.tolist(),
                    fft  = data.tolist()
            )
            source.stream(new_data, data.shape[0])
            
#%%
# Function to change the window of sampling (deltaF = 1/T)
def changeT(attr,old,new):
    streamer.T = new
    streamer.init_buff() # reinit the buffer

#%%
# Function that is callled on button press to detect the fundamental + make the fundamental + harmonic plots
def detect_base_freq(attr,old,new):
    
    #Detect Fundamental
    data = pd.DataFrame(source.data)
    ix_peak_rough = peakutils.indexes(data['fft'],min_dist=5*streamer.T) # 5 Hz distance to other peaks
    if len(ix_peak_rough) == 0:
        return
    
    ix_max  = data['fft'].idxmax()
    
    candidates = data['freq'].iloc[ix_max] / ((np.array(range(20))+1)/streamer.T)
    candidates = np.flip(candidates,axis=0)
    np.append(candidates,-1)

    
    for cand in candidates:
        autopeak = data['freq'].iloc[ix_peak_rough]
        candidatevalues =np.abs(1-cand/autopeak)
        closest = np.min(candidatevalues)
        if closest<0.05: #someone is closer than 5% to the current max freq
            print('good candidate found %.2f to peak %.2f'%(cand,autopeak[candidatevalues.idxmin()]))
            break
    
    print('winner cand: %.2f'%(cand))

    
    # add 
    new_data = dict(
            freq = data['freq'].iloc[ix_peak_rough],
            fft  = data['fft'].iloc[ix_peak_rough])
    sourcepeak.stream(new_data,ix_peak_rough.shape[0])
    
    #%% Plot zoomed in versions of fundamental + 2x fundamental
    f_f1 = cand
    f_f2 = 2*f_f1
    # TODO: make this a slider
    xaxiswidth = 30 

    # Get the respective data
    data_f1 = data.query("freq>%f&freq<=%f"%( f_f1 - xaxiswidth/2, f_f1 + xaxiswidth/2))
    data_f2 = data.query("freq>%f&freq<=%f"%( f_f2 - xaxiswidth/2, f_f2 + xaxiswidth/2))
    
    # udate it in the plot
    source_f1.stream(data_f1,data_f1.shape[0])
    source_f2.stream(data_f2,data_f2.shape[0])
    

    # find the peaks on this subset (in order to fold the fundamental to the harmonic)
    ix_peaks_f1 = peakutils.indexes(data_f1['fft']) 
    ix_peaks_f2 = peakutils.indexes(data_f2['fft']) 
    
    # get the peak data values
    data_line_f1 = data_f1.iloc[ix_peaks_f1].assign(color='blue')
    data_line_f2 = data_f2.iloc[ix_peaks_f2].assign(color='red')
    # fold up the fundamental to the harmonic 2
    data_line_f2 = pd.concat([data_line_f2,data_f2.iloc[ix_peaks_f1].assign(color='blue')],ignore_index=True)
    
    # add the labels
    
    
    
    data_line_f1.loc[:,'label'] =data_line_f1.apply(lambda row_: converter.freq_to_name(row_['freq']),axis=1)
    data_line_f2.loc[:,'label'] =data_line_f2.apply(lambda row_: converter.freq_to_name(row_['freq']),axis=1)
    
    # concat to display both (we need to change the color later)
    #data_line_f2 =pd.concat([data_line_f2,data_line_f1_f2],ignore_index=True)
    
    source_line_f1.stream(data_line_f1,data_line_f1.shape[0])
    source_line_f2.stream(data_line_f2,data_line_f2.shape[0])
    
    
    
    cycledur = int(1/100*streamer.RATE) # lowest frequency
    signal = list(streamer.buff)
    signal = signal[-(2*cycledur):]
        
    time = list(range(len(signal)))
    
    new_data_signal = dict(
                    time = time,
                    signal= signal
                    )
         
    source_signal.stream(new_data_signal,len(time))
    
    
    
#%%
# Bokeh Slider that easily allows to change the timer
length_slider = Slider(value=streamer.T,start=0.1, end=20, step=.1,
                    title="Integration Time")
length_slider.on_change('value',changeT)

def changeConcertPitch(attr,old,new):
    converter.concertpitch=new
concertpitch_slider = Slider(value=converter.concertpitch,start=425, end=445, step=1,
                    title="Concert Pitch")
concertpitch_slider.on_change('value',changeConcertPitch)


# This button allows to lock in the current data
detect_button = Button()
detect_button.on_change('clicks',detect_base_freq)

#%%
# make the grid & add the plots
curdoc().add_root(gridplot([p,widgetbox(length_slider,concertpitch_slider,detect_button,width=400)],[p_time,None],[p_f1,p_f2]))
# update every 100ms
curdoc().add_periodic_callback(update, 100)
curdoc().title = "Bandoneon Tuner"