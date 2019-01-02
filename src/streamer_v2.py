# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 07:36:24 2018

@author: behinger
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 10:54:26 2018

@author: behinger
"""

#import matplotlib.pyplot as plt
import numpy as np
from os.path import dirname, join
import audiostream
import pandas as pd
import numpy as np

from scipy.stats import entropy
np.random.seed(1)

from bokeh.layouts import row, column,widgetbox
from bokeh.models import ColumnDataSource, Slider, Button,LabelSet,CheckboxButtonGroup,Paragraph,DataTable, TableColumn,Span,CustomJS

from bokeh.plotting import curdoc, figure
#from bokeh.driving import count

import hz_to_scale
import peakutils

class bokeh_tuner():
    def __init__(self,pitch=442,xrange=20):
        self.xrange = xrange
        self.highpass = 50
        self.text = ''
        self.entropythreshold = 7.5 # mostly tested with T=4
        self.T = 4
        
        self.loudrange = 10000 # the y-axis for the time signal
        self.freezeInset = False
        self.autoupdate = False
        
        self.init_data_sources()
        self.init_plots()
        
        self.audiostreamer = audiostream.AudioStream(T=self.T)
        self.converter = hz_to_scale.hz_to_scale(pitch)
        
    def init_plots(self):
            
        
            # The continuous signal plot (last X samples)
            self.p_signal = figure(plot_height=250, tools="xpan,xwheel_zoom,xbox_zoom,reset" ,y_range=(-self.loudrange,self.loudrange))
            self.p_signal.line(x='time', y='signal', line_width=3, color='navy', source=self.sources['signal'])
            
            
            # main FFT figure
            self.p_fft = figure(plot_height=250, tools="xpan,xwheel_zoom,xbox_zoom,reset",x_axis_type="log")
            self.p_fft.line(x='freq', y='fft', line_width=3, color='navy', source=self.sources['fft'])             # We add the fft power spectra
            #self.p_fft.circle(x='freq', y='fft', color='navy', source=self.sources['fft'])             # We add the fft power spectra
            self.p_fft.circle(x='freq',y='fft',color='red',source=self.sources['fftpeak'])# After we identified peaks (to detect the fundamental), we add the peaks in here
            
            # This plot is a zoomed in version of the fundamental
            self.p_fft_f1 = figure(plot_height=250, tools="xpan,xwheel_zoom,xbox_zoom,reset" )
            #self.p_fft_f1.circle(  x='freq', y='fft', color='navy', source=self.sources['fft_f1'])
            self.p_fft_f1.line(  x='freq', y='fft', line_width=3, color='navy', source=self.sources['fft_f1'])
            self.p_fft_f1.circle(x="freq", y='fft', color='color',source=self.sources['fftpeak_f1'],size=7)
            
            # this plot is a zoomed in version of 2x the fundamental
            self.p_fft_f2 = figure(plot_height=250, tools="xpan,xwheel_zoom,xbox_zoom,reset" )
            self.p_fft_f2.line(  x='freq', y='fft', line_width=3, color='navy', source=self.sources['fft_f2'])
            #self.p_fft_f2.circle(  x='freq', y='fft', line_width=3, color='navy', source=self.sources['fft_f2'])
            self.p_fft_f2.circle(x="freq", y='fft', color='color',source=self.sources['fftpeak_f2'],size=7)
            
            self.p_fft_f1.circle(x='perfectFreq', y='fft', color='black',  line_width=3,source=self.sources['fftpeak_f1'])
            self.p_fft_f2.circle(x='perfectFreq', y='fft', color='black',  line_width=3,source=self.sources['fftpeak_f2'])
            
            self.p_fft_f1.add_layout(LabelSet(x='freq', y='fft', text_color='color',text='label', level='glyph',
                          x_offset=15, y_offset=-15, source=self.sources['fftpeak_f1'], render_mode='canvas'))
            self.p_fft_f2.add_layout(LabelSet(x='freq', y='fft', text_color='color',text='label', level='glyph',
                          x_offset=15, y_offset=-15, source=self.sources['fftpeak_f2'], render_mode='canvas'))

            self.p_text = Paragraph(text=self.text, width=200, height=100)
            
            self.p_saved =DataTable(source=self.sources['savednotes'], columns=[TableColumn(field='basenote',title='Basis Note'),
                                                                                TableColumn(field="note",title="note"),
																				TableColumn(field="perfectFreq",title="IdealFrequenz"),
                                                                                TableColumn(field='freq',title="PeakFrequenz"),
                                                                                TableColumn(field='cent',title='Cent Abweichung')], width=400, height=400)
            print('V1.1')
    def init_data_sources(self):
        self.sources = {
                            
            'fft': ColumnDataSource(dict(freq=[], fft=[])), # was source
            'signal': ColumnDataSource(dict(time=[],signal=[])), # was sourcesignal
            
            'fftpeak':ColumnDataSource(dict(freq=[],fft=[])) ,
            'fft_f1': ColumnDataSource(dict(freq=[],fft=[],index=[])),
            'fft_f2': ColumnDataSource(dict(freq=[],fft=[],index=[])),

            'fftpeak_f1':ColumnDataSource(dict(freq=[],fft=[],index=[],color=[],label=[],perfectFreq=[])),
            'fftpeak_f2':ColumnDataSource(dict(freq=[],fft=[],index=[],color=[],label=[],perfectFreq=[])),
            'savednotes':ColumnDataSource(dict(basenote=[],note=[],perfectFreq = [],freq = [],cent=[]))
                }

    def fft_update(self):
        # get the FFT
        data = self.audiostreamer.calc_fft()
        
        if data is None:
            return
        freqs = (np.array(range(data.shape[0]))+1) / self.audiostreamer.T

        ix = freqs>self.highpass
        freqs = freqs[ix]
        data  = data[ix]

        # If data remains, add it to the power spectra
        if type(data) != type(None):
            new_data = dict(
                    freq = freqs.tolist(),
                    fft  = data.tolist()
            )
            self.sources['fft'].stream(new_data, data.shape[0])

        signal = list(self.audiostreamer.buff[::10])
            
        time = list(range(len(signal)))
        
        new_data_signal = dict(
                        time = time,
                        signal= signal
                        )
             
        self.sources['signal'].stream(new_data_signal,len(time))
        
        # if we do not want to freeze the signal, we update the small insets
        if not self.freezeInset:
            self.detect_base_freq()
            
        if self.autoupdate:
            self.entropy_autoupdate()
            
    def changeT(self,attr,old,new):
            self.T = new
            self.audiostreamer.T = self.T
            self.audiostreamer.init_buff() # reinit the buffer

    #%%
    # Function that is callled on button press to detect the fundamental + make the fundamental + harmonic plots
    def detect_base_freq_bokeh(self,attr,old,new):
        self.analyse_and_save()

    def detect_base_freq(self):

        #Detect Fundamental
        data = pd.DataFrame(self.sources['fft'].data)
        ix_peak_rough = peakutils.indexes(data['fft'],min_dist=5*self.audiostreamer.T) # 5 Hz distance to other peaks
       
        if len(ix_peak_rough) == 0:
            return(None,None)
        #print('detection started')
        ix_max  = data['fft'].idxmax()
        
        candidates = data['freq'].iloc[ix_max] / ((np.array(range(20))+1)/self.audiostreamer.T)
        candidates = np.flip(candidates,axis=0)
        np.append(candidates,-1)
    
        
        for cand in candidates:
            autopeak = data['freq'].iloc[ix_peak_rough]
            candidatevalues =np.abs(1-cand/autopeak)
            closest = np.min(candidatevalues)
            if closest<0.05: #someone is closer than 5% to the current max freq
                #print('good candidate found %.2f to peak %.2f'%(cand,autopeak[candidatevalues.idxmin()]))
                break 
        
        # add 
        new_data = dict(
                freq = data['freq'].iloc[ix_peak_rough],
                fft  = data['fft'].iloc[ix_peak_rough])
        self.sources['fftpeak'].stream(new_data,ix_peak_rough.shape[0])
        
        
        #%% Plot zoomed in versions of fundamental + 2x fundamental
        f_f1 = cand
        f_f2 = 2*f_f1
        xaxiswidth = self.xrange 
    
        # Get the respective data
        data_f1 = data.query("freq>%f&freq<=%f"%( f_f1 - xaxiswidth/2, f_f1 + xaxiswidth/2))
        data_f2 = data.query("freq>%f&freq<=%f"%( f_f2 - xaxiswidth/2, f_f2 + xaxiswidth/2))
        
        # udate it in the plot
        self.sources['fft_f1'].stream(data_f1,data_f1.shape[0])
        self.sources['fft_f2'].stream(data_f2,data_f2.shape[0])
        
    
        # find the peaks on this subset (in order to fold the fundamental to the harmonic)
        ix_peaks_f1 = peakutils.indexes(data_f1['fft'])#,min_dist=0.5*self.audiostreamer.T) 
        ix_peaks_f2 = peakutils.indexes(data_f2['fft'])#,min_dist=0.5*self.audiostreamer.T) 
        
        # get the peak data values
        fftpeak_f1 = data_f1.iloc[ix_peaks_f1].assign(color='blue')
        fftpeak_f2 = data_f2.iloc[ix_peaks_f2].assign(color='red')
        # fold up the fundamental to the harmonic 2
        if ix_peaks_f1.shape[0]>0:
            fftpeak_f2_both = pd.concat([fftpeak_f2,data_f2.iloc[ix_peaks_f1].assign(color='blue')],ignore_index=True)
            
        
        # add the labels
        
        
        if fftpeak_f1.shape[0]> 0:
            fftpeak_f1.loc[:,'label']      =fftpeak_f1.apply(     lambda row_: self.converter.freq_to_name(row_['freq']),axis=1)
            fftpeak_f2_both.loc[:,'label'] =fftpeak_f2_both.apply(lambda row_: self.converter.freq_to_name(row_['freq']),axis=1)
            fftpeak_f1.loc[:,'perfectFreq']      = fftpeak_f1.apply(     lambda row_: self.converter.name_to_freq(row_['label'].partition(':')[0]),axis=1)
            fftpeak_f2_both.loc[:,'perfectFreq'] = fftpeak_f2_both.apply(lambda row_: self.converter.name_to_freq(row_['label'].partition(':')[0]),axis=1)
        else:
            fftpeak_f1.loc[:,'label'] = ''
            fftpeak_f2_both.loc[:,'label'] = ''
            fftpeak_f1.loc[:,'perfectFreq'] = np.nan
            fftpeak_f2_both.loc[:,'perfectFreq'] = np.nan
                        
        
        self.sources['fftpeak_f1'].stream(fftpeak_f1,fftpeak_f1.shape[0])
        self.sources['fftpeak_f2'].stream(fftpeak_f2_both,fftpeak_f2_both.shape[0])
        
        
        
        
        def analyseFreq(n):
            #print(n)
            return(pd.Series({'cent':self.converter.number_cent_difference(n['number']),
                              'freq':n['freq'],
                              'note':self.converter.get_base(n['number'])+str(self.converter.get_octave(n['number'])),
							  'perfectFreq':np.round(self.converter.name_to_freq(self.converter.get_base(n['number'])+str(self.converter.get_octave(n['number']))),2)})
            )
            
        fftpeak_f1['number'] =fftpeak_f1.apply(lambda x:self.converter.freq_to_number(x['freq']),axis=1)
        fftpeak_f2['number'] =fftpeak_f2.apply(lambda x:self.converter.freq_to_number(x['freq']),axis=1)
        
        f1_analysed          =fftpeak_f1.apply(lambda n: analyseFreq(n),axis=1)
        f2_analysed          =fftpeak_f2.apply(lambda n: analyseFreq(n),axis=1) 
        
        
        return(f1_analysed,f2_analysed)
        
    def changeConcertPitch(self,attr,old,new):
        self.converter.concertpitch=new    
    
    def entropy_autoupdate(self):
        data = pd.DataFrame(self.sources['fft'].data)
        ent = entropy(data['fft'])
        if ent < self.entropythreshold:
            self.analyse_and_save()
    def analyse_and_save(self):
        f1_analysed,f2_analysed = self.detect_base_freq()
        if f1_analysed is None:
            return
        
        # mark f2's that are 2x f1's
        
        f12_freq = set(f1_analysed.freq*2).intersection(set(f2_analysed.freq)) # these are freqs that míght be only harmonies
        
        
        def f12_freq_function(row):
            if row['freq'] in f12_freq:
                string = ' x'
            else:
                string=''
            return(row['note']+string)
            
        f2_analysed.loc[:,'note'] = f2_analysed.apply(lambda row: f12_freq_function(row),axis=1)
        basenote = f1_analysed.iloc[0]['note']
        
        savednotes = pd.DataFrame(self.sources['savednotes'].data)
        savednotes = savednotes.set_index('basenote')
        try:
            savednotes = savednotes.drop(basenote,axis=0)
        except KeyError:
            print('KeyError')
            pass
        #'savednotes':ColumnDataSource(dict(note=[],hz_f1 = [], hz_f2 = [],diff_f1 = [], diff_f2 = []))
        f1_analysed.loc[:,'basenote'] = basenote
        f2_analysed.loc[:,'basenote'] = basenote
        
        newnotes = pd.concat([f1_analysed, f2_analysed])
        
        newnotes = newnotes.set_index('basenote')
        
        print(savednotes)
        print(newnotes)
        savednotes = pd.concat([savednotes,newnotes])
        
        savednotes_dict = savednotes.to_dict('list')
        savednotes_dict['basenote'] = savednotes.index 
		
        self.sources['savednotes'].data = savednotes_dict
        
    def startstop_autoupdate(self,attr,old,new):
        print(attr,old,new)
        if 0 in new:
            print('starting autoupdate')
            self.autoupdate = True
        else:
            print('removing autoupdate')
            self.autoupdate = False
            
        if 1 in new:
            print('freezing inset')
            self.freezeInset = True
        else:
            print('unfreezing inset')
            self.freezeInset = False
    def change_xrange(self,attr,old,new):
        self.xrange = new
    def save_table(self,attr,old,new):
        print("saving table")
        
        
#%%
                
bt = bokeh_tuner()
# Bokeh Slider that easily allows to change the timer
length_slider = Slider(value=bt.audiostreamer.T,start=0.1, end=20, step=.1,
                    title="Integration Time (s)")
length_slider.on_change('value',bt.changeT)


concertpitch_slider = Slider(value=bt.converter.concertpitch,start=430, end=450, step=1,
                    title="Concert Pitch")
concertpitch_slider.on_change('value',bt.changeConcertPitch)


fundamental_xrange = Slider(value=bt.xrange,start=5, end=100, step=1,
                    title="X-range")
fundamental_xrange.on_change('value',bt.change_xrange)




checkbox_button_group = CheckboxButtonGroup(
        labels=["Auto-Save to Table","FreezeInset"], active=[])
checkbox_button_group.on_change('active',bt.startstop_autoupdate)


# This button allows to lock in the current data
detect_button = Button(label='Manual Detect and add to Table')    
detect_button.on_change('clicks',bt.detect_base_freq_bokeh)


save_button = Button(label='Save Current Table')    
#save_button.on_change('clicks',bt.save_table)
save_button.callback =  CustomJS(args=dict(source=bt.sources['savednotes']),
                           code=open(join(dirname(__file__), "download.js")).read())


#%%
# make the grid & add the plots
widgets = widgetbox(length_slider,concertpitch_slider,fundamental_xrange,detect_button,save_button,checkbox_button_group,width=400)
#curdoc().add_root(row([
#        column(bt.p_fft,bt.p_fft_f1,widgets),
#        column(bt.p_signal,bt.p_fft_f2),
#        column(bt.p_saved)]
#        ))

curdoc().add_root(row([column([bt.p_fft,bt.p_fft_f1,bt.p_fft_f2]),
                  column([widgets,bt.p_saved])]))

# update every 100ms
curdoc().add_periodic_callback(bt.fft_update, 100)

curdoc().title = "Bandoneon Tuner"