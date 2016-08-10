#import csv
import numpy as np
import scipy.signal as signal
#from bokeh.plotting import figure, output_file, show
import matplotlib.pyplot as plt

class GSR:
    
    def __init__(self, databuffer, fs):
        """ import GSR data from arduino """
        self.gsr=np.array(databuffer)        
        self.fs = fs
        self.T = 1./fs 
        self.time=(np.arange(len(self.gsr)))*self.T
    
    def filter(self):
        #output_file("gsrfilter.html")
        #p = figure()
        #p.line(self.time,self.gsr,line_color='red')
        wl = 50.0/self.fs
        b,a = signal.butter(3,wl,'lowpass')
        self.gsr = signal.lfilter(b, a, self.gsr)
        #plt.plot(self.gsr)
#        p.line(self.time,self.gsr,line_color='blue')
#       show(p)
        return

 
    def feature(self,baseline, time):
        """ feature detection """
        self.filter()
        timeperiod = 1
        resptime = 0
        for i in range(0,len(self.gsr)-timeperiod*self.fs, timeperiod*self.fs):
            gsr5s = self.gsr[i:i+timeperiod*self.fs]
            pos_threshold = 1.1*baseline
            ind_pos = np.nonzero(gsr5s > pos_threshold)
            pos_duration = len(gsr5s[ind_pos])*self.T
            if pos_duration >0.9 :
                peak = np.amax(self.gsr[ind_pos])
                resptime += 1
            
            neg_threshold = 0.8*baseline
            ind_neg = np.nonzero(gsr5s < neg_threshold)
            neg_duration = len(gsr5s[ind_neg])*self.T
            if neg_duration >0.9 and pos_duration>0.9:
                valley = np.amin(self.gsr[ind_neg])
            elif neg_duration >0.9 and not (pos_duration>0.9):
                valley = neg_duration*self.T
                resptime += 1    
        return (resptime/time)


#------------MAIN--------------------#
#import collections
#import copy
#
#if __name__=='__main__':
#    x=np.genfromtxt('willgsrperf.txt')
#    gsrall=x[:]
#    gsrall2=GSR(gsrall,250)
#    gsrall2.feature(1.6, 10)
    
#    fs = 250
#    gsrcali=[]
#    for i in range(0,10*fs):
#        gsrcali.append(gsrall[i])
#        baseline = np.mean(gsrcali)
#    print "baseline: ", baseline
#    
#    gsr10s=[]
#    runtime = 50
#    gsrqueue=collections.deque(maxlen=10*fs)
#    for i in range(0,runtime*fs,10*fs):
#        print i
#        for j in range(0,fs*10):
#            gsrqueue.append(gsrall[i+j])
#        gsr10s=copy.deepcopy(gsrqueue)
#
#        if len(gsr10s)==fs*10:
#            gsr = GSR(gsr10s,fs)
#            gsr=gsr.filter()
#            gsrfeatures=gsr.feature(baseline)
#        print gsrfeatures
#        plt.figure()
#        plt.plot(gsr10s)
#        
#    plt.show(block=False)
#    
