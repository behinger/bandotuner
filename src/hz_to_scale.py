#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 10:05:02 2018

@author: behinger
"""

import numpy as np
NOTE_NAMES = 'C C# D D# E F F# G G# A A# H'.split()

######################################################################
# These three functions are based upon this very useful webpage:
# https://newt.phys.unsw.edu.au/jw/notes.html

# Number refers to midinumber

class hz_to_scale:
    def __init__(self,concertpitch=440):
        self.concertpitch = concertpitch
        
    def freq_to_number(self,f): 
        return 69 + 12*np.log2(f/self.concertpitch)
    
    def number_to_freq(self,n): 
        return self.concertpitch * 2.0**((n-69)/12.0)
    
    def number_to_name(self,n): 
        return  np.char.array(self.get_base(n)) +  np.char.array(self.get_octave(n).astype(str))+ ':'+ np.char.array(self.number_cent_difference(n).astype(str))
    
    def get_base(self,n):
        n = np.round(n).astype(int)
        return(np.array(NOTE_NAMES)[n % 12])
    def get_octave(self,n):
        n = np.round(n)
        return(np.floor(n/12-1).astype(int))
    def number_cent_difference(self,actual,ref=None):
        if ref is None:
            ref = np.round(actual)
        #print(ref,actual)
        ref = self.number_to_freq(ref)
        actual = self.number_to_freq(actual)
        return(self.freq_cent_difference(ref,actual))
        
        
    def freq_cent_difference(self,ref,actual):
        centfromA_ref = 1200*np.log2(ref/self.concertpitch)
        centfromA_actual = 1200*np.log2(actual/self.concertpitch)
        return(-np.round(centfromA_ref - centfromA_actual).astype(int))
        
    def freq_to_name(self,f):
        n = self.freq_to_number(f)
        return(self.number_to_name(n))
    def name_to_idealnumber(self,name):
        #G4:5
        name = np.char.array(name)
        note = name.split(':')
        basen = np.char.array([n[0] for n in note])
        octav = np.asarray(basen.lstrip(['ABCDEFGHB#b'])).astype(int)
        centdeviation= np.asarray([n[1] for n in note]).astype(int) # currently ignored
        basen = np.array([NOTE_NAMES.index(n) for n in basen.rstrip([':1234567890']).tolist()])
        n = basen + 12*(1+octav)
        return(n)
    def name_to_idealfreq(self,name):
        n = self.name_to_idealnumber(name)
        return(self.number_to_freq(n))