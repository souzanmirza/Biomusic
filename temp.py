# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 15:35:42 2016

@author: Souzan

This works March 25
"""

# -*- coding: utf-8 -*-

import numpy as np

class TEMP:

    def __init__(self, databuffer):
        """ import temp data from arduino """
        self.temp=databuffer        
#
#    def __init__(self, filename):
#        with open(filename,'rb') as csvfile:
#            data = csv.reader(csvfile, delimiter=',')
#            x = list(data)
#        self.temp = np.array(x).astype('float')
#        """ import ECG data with filename """
#        
    def voltage2temp(self):
        avgvoltage=np.mean(self.temp)
        Rt=(10000*avgvoltage)/(5-avgvoltage)
        temp=-51.642*np.log10(Rt) + 232.21
        return float(temp)	

        
#--------------------Main------------------------#
#        
#if __name__ == '__main__':
#    import time
#    start_time = time.time()
#    x = np.genfromtxt('qiantempmarch28-hand-putonafter30s.txt')
#    test=TEMP(x)
#    #test.filter_temp()
#    plt.figure(1)
#    plt.plot(test.temp)
#    axes = plt.gca()
#    axes.set_ylim([0,3.3])
#    plt.show()   
#    output=1
#    time=300
#    for i in range(0,time*250,10*250):
#        vals=x[i:i+10*250]
#        len(vals)
#        test=TEMP(vals)
#        dev=float(test.voltage2temp()-output)/output*100
#        output=test.voltage2temp()
#        print i/250,output, dev
    #print 'average temp is',temp  