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
        return self.get_base(n) + str(self.get_octave(n))+ ':'+ str(self.number_cent_difference(n))
    
    def get_base(self,n):
        n = int(round(n))
        return(NOTE_NAMES[n % 12])
    def get_octave(self,n):
        n = int(round(n))
        return(int(round(n/12 - 1)))
    def number_cent_difference(self,actual,ref=None):
        if ref is None:
            ref = int(round(actual))
        #print(ref,actual)
        ref = self.number_to_freq(ref)
        actual = self.number_to_freq(actual)
        return(self.freq_cent_difference(ref,actual))
        
        
    def freq_cent_difference(self,ref,actual):
        centfromA_ref = 1200*np.log2(ref/self.concertpitch)
        centfromA_actual = 1200*np.log2(actual/self.concertpitch)
        return(-int(round(centfromA_ref - centfromA_actual)))
        
    def freq_to_name(self,f):
        n = self.freq_to_number(f)
        return(self.number_to_name(n))