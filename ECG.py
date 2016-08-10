# -*- coding: utf-8 -*-
"""
Created on Thu Feb 04 13:02:27 2016

@author: Souzan

ECG Processing class. This class extracts the HR, Breathing rate and average R 
wave amplitude of an 8s interval.
This function takes around 0.07-0.13s to run.

"""

import numpy as np
import scipy.signal as signal
from detect_peaks import detect_peaks


class ECG:

    def __init__(self, databuffer, fs):
        """ import ECG data from arduino """
        self.ecg=np.array(databuffer)        
        self.fs = fs
        self.T = 1./fs 
        self.time=(np.arange(len(self.ecg)))*self.T
        self.Rpeaks=np.zeros((1,2),dtype=float)
#        self.Speaks=np.zeros((1,2),dtype=float)
        
    def filter_ecg(self):
        ''' remove baseline'''
        fftecg=np.fft.fft(self.ecg)
        step=500.0/len(fftecg)
        s=int(4./step)
        fftecg[0:s]=0
        ecg_b=(np.fft.ifft(fftecg)).real      
        """ highpass filter ecg signal with cutoff frequency """
        b, a = signal.cheby1(2, 1, 2.0/250, 'highpass')
        self.ecg=signal.lfilter(b, a, ecg_b)
        b, a = signal.cheby1(2, 1, 60.0/250, 'lowpass')
        self.ecg=signal.lfilter(b, a, self.ecg)
        
        
    def detect_R_peaks(self):       
        maxpeak=0.33*max(self.ecg)
        locs=detect_peaks(self.ecg, mph=maxpeak, mpd=round(0.3*self.fs))
        Rpeaks=[0]*len(locs)
        for i in range(0,len(locs)):
            Rpeaks[i]=([locs[i],self.ecg[locs[i]]])
        self.Rpeaks=np.array(Rpeaks)

    def QRSdetect(self):
        """ Dectect the R and S in the clean_ecg """
        self.filter_ecg()        
        self.detect_R_peaks()
#        self.detect_S_peaks()
        
    def HR(self):
       '''detect HR using avg of R-R intervals'''
       self.QRSdetect()
       RR_interval=[]
       for i in range(0,len(self.Rpeaks)-1):
           RR_interval.append((self.Rpeaks[i+1][0]-self.Rpeaks[i][0])/self.fs)
       return round(1/np.mean(RR_interval)*60)
       
    def R_amp(self):
        #this might be shifty... need to figure out what the voltage bounds is for this
        #number to make sense
        return np.mean(self.Rpeaks[:,1])
        
    def Resp_Rate(self):
        """works if there is the same number of R and S peaks"""     
        '''need atleast 3 breaths >10s to get an accurate value, 6s is too little, might 
        need to make another ecg object to do it or else HR will change too slowly'''
        Resp=[]
        for i in range(0,len(self.Rpeaks)):
            Resp.append([self.Rpeaks[i][0], (self.Rpeaks[i][1])])    
        Resp_rate=np.array(Resp)  
        intervals=self.period(Resp_rate)
        if intervals==0:
            return 0
        if len(intervals)==1:
            return round(60/intervals[0]*self.T)
        else:              
            return round(60/(np.mean(intervals)*self.T))
    
        
    def period(self,Resp_rate):   
        """finds the period of the breathing rate but identifying the points above the midline. 
        Then for each sequential set of data points the time associated with the maximum value is 
        found and the means of the peak intervals is calculated as the breathing rate"""
        avg=np.mean(Resp_rate[:,[1][0]])     
        aboveavg=[]
        for i in range(0,len(Resp_rate)):
            if Resp_rate[i][1]>avg:
                aboveavg.append([i, Resp_rate[i][0], Resp_rate[i][1]])
        i=0
        breathint=[]
        if len(aboveavg)<=1:
            breathint=0                           
        else:
            for i in range(0,len(aboveavg)-1):
                    breathint.append(aboveavg[i+1][1]-aboveavg[i][1])
        return breathint