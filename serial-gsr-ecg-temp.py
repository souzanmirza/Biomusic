import threading
from Queue import Queue
import collections
import numpy as np
from HandGSR_freq import GSR 
from ECG import ECG
from temp import TEMP
import copy
from music import music, music_calibration, MusicMapping, ChangeVolume
from bokeh.plotting import figure, output_file, show
from readfromserial2 import readfromserial     
import serial
import scipy.signal as signal
import time


class ProducerThread(threading.Thread):      
    def __init__(self, baseline, runtime, fs):
        threading.Thread.__init__(self)
        self.runtime=runtime
        self.baseline=baseline
        self.oldvol=94;
        self.fs=fs
    def run(self):
        print 'start'
        global factor_ecg,factor_gsr, ser
        i=0
        timeperiod=10.0
        shift=8         
        ecgqueue=collections.deque(maxlen=timeperiod*self.fs)
        gsrqueue=collections.deque(maxlen=timeperiod*self.fs)
        tempqueue=collections.deque(maxlen=timeperiod*self.fs)
        gsr10s=[]
        ecg10s=[]
        temp10s=[]
        while i<=self.runtime:
            start_time=time.time()
            for j in range(0,shift*self.fs*3):
                #assuming consecutive values are both not garbage
                val=readfromserial(ser)
                if val=='0':
                    val=readfromserial(ser)
                if val[0]=='e':
                     ecgqueue.append(val[1])
                if val[0]=='g':
                     gsrqueue.append(val[1])
                if val[0]=='t':
                    tempqueue.append(val[1])
##                else:
##                    val=readfromserial(ser)  
            print 'time taken to read from serial:', time.time()-start_time
            gsr10s=copy.deepcopy(gsrqueue)
            ecg10s=copy.deepcopy(ecgqueue)
            temp10s=copy.deepcopy(tempqueue)
            print 'len ECG: ', len(ecg10s), 'len GSR: ', len(gsr10s), 'len temp: ', len(temp10s)
            
            #initialize 
            gsrfeatures=0
            HRdeviation=0
            #Rampdeviation=0
            Respratedeviation=0
            tempdeviation=0 
            
            if len(gsr10s)==self.fs*timeperiod:
                gsr = GSR(gsr10s,self.fs)
                gsrbaseline=self.baseline[0]
                gsrfeatures = gsr.feature(gsrbaseline, timeperiod)
                factor_gsr.put(gsrfeatures)
#                print 'GSR freq: ', gsrfeatures
                self.baseline[0]=self.baseline[0]
                
            #ECG data sent to ECGqueue                 
            if len(ecg10s)==self.fs*timeperiod:
                ecg = ECG(ecg10s,self.fs)
                HRdeviation=(ecg.HR()-baseline[1])/baseline[1]                
                #Rampdeviation=(ecg.R_amp()-baseline[2])/baseline[2] 
                Respratedeviation=(ecg.Resp_Rate()-baseline[2])/baseline[2] 
                #factor_ecg.put([HRdeviation, Rampdeviation])  
                factor_ecg.put([HRdeviation, Respratedeviation])   
#                print 'HR, HRdev: ', (ecg.HR(), HRdeviation)
                self.baseline[1]=ecg.HR()
                #self.baseline[2]=ecg.R_amp()
                Resprate=ecg.Resp_Rate()
                if Resprate==0:
                    self.baseline[2]=self.baseline[2]
                else:
                    self.baseline[2]=Resprate

            #TEMP data
            if (len(temp10s)==self.fs*timeperiod):
                len(temp10s)
                new=TEMP(temp10s).voltage2temp()
                tempdeviation=float(new-self.baseline[3])/self.baseline[3]*100
                self.baseline[3]=new
#                print 'temp:', i/250,self.baseline[3], tempdeviation    
                factor,newvol=MusicMapping(tempdeviation).volmapping(self.oldvol)
#                print factor,newvol
                volume=ChangeVolume()
                volume.setvolume(factor)   
                self.oldvol=newvol
                self.baseline[3]=new 
            
            #print "(gsr, HR, resp, temp) dev:", gsrfeatures, HRdeviation, Rampdeviation, tempdeviation, i  
            print "(gsr, HR, resp, temp) dev:", gsrfeatures, HRdeviation, Respratedeviation, tempdeviation, i  

#            print 'baseline is (gsr baseline, ecg HR, ecg Resp_Rate, temp): ', self.baseline

            i=i+shift
            
        print 'exit producer'
        event.set()
        ser.close()
        return        
        
class ConsumerThreadGSR(threading.Thread):
    def __init__(self, Fs):
        threading.Thread.__init__(self)
        self.Fs=Fs
    def run(self):
        global factor_gsr
        factor = 0
        while (not event.is_set()):
            if factor_gsr.qsize()>1:
                n = factor_gsr.get()
                factor_gsr.task_done()
#                print "Get: GSR deviation =", n
    
                snd = flute.popleft()
                mapping = MusicMapping(n)
                factor = mapping.pitchmappingGSR(factor)
                if factor == 0:
                    data = snd
                else:
                    m = music(snd, self.Fs)
                    data = m.pitchshifter(factor)
                 #filtering
                wl=8000.0/self.Fs
                b,a = signal.butter(3,wl,'lowpass')
                data = (signal.lfilter(b, a, data)).astype('int16')
                
                print "GSR factor: ", factor, time.time()-start_time
                flute_queue.put([factor, data])
                flute.append(snd)
                
        while (event.is_set() and not factor_gsr.empty()):
            n = factor_gsr.get()
            factor_gsr.task_done()
#            print "Get: GSR deviation =", n

            snd = flute.popleft()
            mapping = MusicMapping(n)
            factor = mapping.pitchmappingGSR(factor)
            if factor == 0:
                data = snd
            else:
                m = music(snd, self.Fs)
                data = m.pitchshifter(factor)
             #filtering
            wl=8000.0/self.Fs
            b,a = signal.butter(3,wl,'lowpass')
            data = (signal.lfilter(b, a, data)).astype('int16')
            
            print "GSR pitch: ", factor, time.time()-start_time
            flute_queue.put([factor, data])
            flute.append(snd)
            
        eventFlute.set()
                    
        print 'exit GSR consumer'
        return

class ConsumerThreadGSRtrack(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global start_time
        while (not eventFlute.is_set()):
            if flute_queue.qsize()>1:
                data = flute_queue.get()
                flute_queue.task_done()
                print "\nPlay GSR music (pitch)", data[0], time.time()-start_time
                flute_stream.write(data[1].tobytes())
                
        while (eventFlute.is_set() and not flute_queue.empty()):
            data = flute_queue.get()
            flute_queue.task_done()
            print "\nPlay GSR music (pitch)", data[0], time.time()-start_time
            flute_stream.write(data[1].tobytes())
        print 'End GSR stream'
        return

class ConsumerThreadECG(threading.Thread):
    def __init__(self, Fs):
        threading.Thread.__init__(self)
        self.Fs=Fs
    def run(self):
        global factor_ecg
        factor_tempo=1
        factor_pitch=1
        while (not event.is_set()):
            if (factor_ecg.qsize()>1):
                n = factor_ecg.get()
                factor_ecg.task_done()
#                print "Get: ECG deviation =", n
    
                snd = drum.popleft()
                mappingHR = MusicMapping(n[0])
                mappingResp = MusicMapping(n[1])
                factor_tempo = mappingHR.tempomapping(factor_tempo)
                factor_pitch = mappingResp.pitchmappingECG(factor_pitch)
                if factor_pitch == 0:
                    data = snd
                else:
                    mp = music(snd, self.Fs)
                    data = mp.pitchshifter(factor_pitch)
                mt = music(data, self.Fs)
                data = mt.tempo(factor_tempo)
                
                #filtering
                wl=8000.0/self.Fs #change value since music scratches
                b,a = signal.butter(3,wl,'lowpass')
                data = (signal.lfilter(b, a, data)).astype('int16')
                
                print "ECG tempo, pitch: ", factor_tempo, factor_pitch, time.time()-start_time
                drum_queue.put([factor_tempo, factor_pitch, data])
                drum.append(snd)
                
        while (event.is_set() and not factor_ecg.empty()):
            n = factor_ecg.get()
            factor_ecg.task_done()
#            print "Get: ECG deviation =", n

            snd = drum.popleft()
            mappingHR = MusicMapping(n[0])
            mappingResp = MusicMapping(n[1])
            factor_tempo = mappingHR.tempomapping(factor_tempo)
            factor_pitch = mappingResp.pitchmappingECG(factor_pitch)
            if factor_pitch == 0:
                data = snd
            else:
                mp = music(snd, self.Fs)
                data = mp.pitchshifter(factor_pitch)
            mt = music(data, self.Fs)
            data = mt.tempo(factor_tempo)

            #filtering
            wl=8000.0/self.Fs
            b,a = signal.butter(3,wl,'lowpass')
            data = (signal.lfilter(b, a, data)).astype('int16')
             
            print "ECG tempo, pitch: ", factor_tempo, factor_pitch, time.time()-start_time
            drum_queue.put([factor_tempo, factor_pitch, data])
            drum.append(snd)
            
        eventDrum.set()
                    
        print 'exit ECG consumer'
        return

class ConsumerThreadECGtrack(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global start_time
        while (not eventDrum.is_set()):
            if drum_queue.qsize()>1:
                data = drum_queue.get()
                drum_queue.task_done()
                print "\nPlay ECG music (tempo,pitch)",data[0], data[1], time.time()-start_time
                drum_stream.write(data[2].tobytes())
                
        while (eventDrum.is_set() and not drum_queue.empty()):
            data = drum_queue.get()
            drum_queue.task_done()
            print "\nPlay ECG music (tempo,pitch)", data[0], data[1], time.time()-start_time
            drum_stream.write(data[2].tobytes())
        print 'End ECG stream'
        return

class Calibration():
    def __init__(self,fs,ser):
        self.fs=fs
        self.ser = ser
    def calibrate(self):
        print 'start baseline'
        caliperiod=15
        ecgcali=[]
        gsrcali=[]
        tempcali=[]
        i=0
        for i in range(self.fs*2*3):
            '''skip reading the first 2 seconds when the arduino turns on, 
            or else gsr baseline will be wrong'''
            val=readfromserial(self.ser)
        for i in range(self.fs*caliperiod*3):
            val=readfromserial(self.ser)
            if val=='0':
                val=readfromserial(ser)
            if val[0]=='e':
                 ecgcali.append(val[1])
            if val[0]=='g':
                 gsrcali.append(val[1])
            if val[0]=='t':
                tempcali.append(val[1])
##            else:
##                val=readfromserial(self.ser)
##        print gsrcali
##        print len(ecgcali)
        ecg=ECG(ecgcali,self.fs)
        temp=TEMP(tempcali).voltage2temp()
        print len(ecgcali), len(gsrcali), len(tempcali)
        baseline=[np.mean(gsrcali), ecg.HR(), ecg.Resp_Rate(),temp]    
        output_file("signal-calibration.html")
        p = figure()
        # add some renderers
        ecgtime=range(0,len(ecgcali))
        gsrtime=range(0,len(gsrcali))
        temptime=range(0,len(tempcali))        
        p.line(ecgtime,ecgcali,line_color='blue')
        p.line(gsrtime,gsrcali,line_color='red')
        p.line(temptime,tempcali,line_color='green')
        # show the results
        show(p)
        print baseline
        print 'end baseline'
        return baseline
        
#------------MAIN--------------------#
if __name__=='__main__':
    global factor_gsr, factor_ecg, music_queue
    global ser
    global flute, drum, flute_stream, drum_stream
    global Fs
    global start_time
    ser=serial.Serial('COM8',baudrate=57600, timeout=None)
    factor_gsr= Queue()
    factor_ecg= Queue()
    flute_queue = Queue()
    drum_queue = Queue()
    mf = music_calibration('Flute_Sound_Effect_4.wav', 10)
    md = music_calibration('pianoquiet.wav', 10)
    flute,Fs = mf.music_cali()
    drum,Fs = md.music_cali()
    flute_stream = mf.create_stream()
    drum_stream = md.create_stream()   
    import time
#    start_time=time.time()
    event=threading.Event()
    eventFlute=threading.Event()
    eventDrum=threading.Event()
    baseline=Calibration(250,ser).calibrate()
    donecalibration=input('Done Calibration? Enter 0 or 1: ')
    while not donecalibration:
       baseline=Calibration(250,ser).calibrate()
       donecalibration=input('Done Calibration? Enter 0 or 1: ')
    start_time=time.time()
    y=ProducerThread(baseline,60,250)
    ecg=ConsumerThreadECG(Fs)
    ecgtrack=ConsumerThreadECGtrack()
    gsr=ConsumerThreadGSR(Fs)
    gsrtrack=ConsumerThreadGSRtrack()
    y.start()
    ecg.start()
    ecgtrack.start()
    gsr.start()
    gsrtrack.start()
    y.join()
    ecg.join()
    ecgtrack.join()
    gsr.join()
    gsrtrack.join()
    print "time taken:", time.time()-start_time
    print 'Exit Main Thread'

    
