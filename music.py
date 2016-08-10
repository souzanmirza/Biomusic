import librosa.effects as effects
import volumecontroller as volcon
import scipy.io.wavfile as wv
import collections
from pyaudio import PyAudio, paInt16
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

class music:

    def __init__(self,snd_data, Fs):
        self.Fs = Fs
        self.snd_array = snd_data


    def tempo(self,factor):
        """ rate : float > 0 
            If rate > 1, then the signal is sped up.
            If rate < 1, then the signal is slowed down."""
        tempo_audio = effects.time_stretch(self.snd_array, factor)
#        print 'END TEMPO'
        return tempo_audio
        
    def pitchshifter(self, n):
        """ Shift the pitch by n semitones
            n_steps : float"""
        ps_audio = effects.pitch_shift(self.snd_array, self.Fs, n)
#        if n>0:        
#            wl =6000.0/self.Fs
#            b,a = signal.butter(3,wl,'lowpass')
#            ps_audio = signal.lfilter(b, a, ps_audio)
#        if n<0:
#            wl = 6000.0/self.Fs
#            b,a = signal.butter(3,wl,'lowpass')
#            ps_audio = signal.lfilter(b, a, ps_audio)
#        ps_audio=ps_audio.astype('int16')
        return ps_audio
    
    def volume(self,factor):
        """changes the volume of the system's speakers"""
        vol=ChangeVolume()
        vol.setvolume(factor)
#        print 'END VOLUME'
        return

class ChangeVolume():
    def __init__(self):
        self.enumerator = volcon.comtypes.CoCreateInstance(volcon.CLSID_MMDeviceEnumerator,volcon.IMMDeviceEnumerator,
                                           volcon.comtypes.CLSCTX_INPROC_SERVER)
        self.endpoint = self.enumerator.GetDefaultAudioEndpoint( 0, 1 )
        self.volume = self.endpoint.Activate(volcon.IID_IAudioEndpointVolume, volcon.comtypes.CLSCTX_INPROC_SERVER, None )
        
    def setvolume(self,factor):
        self.volume.SetMasterVolumeLevel(factor, None)

class music_calibration:
    def __init__(self, filename, seconds):
        self.filename = filename
        self.seconds = seconds
        
    def music_cali(self):
        Fs, audio = wv.read(self.filename)

        snd_array = []
        cali = self.seconds*Fs
        for i in range(0,len(audio)-cali,cali):
            snd_array.append(audio[:,0][i:i+cali])

        return collections.deque(snd_array),Fs

    def create_stream(self):
        pa = PyAudio()
        return pa.open(format = paInt16,
                     channels = 1,
                     rate = 44100,
                     output = True)

class MusicMapping():
    def __init__(self,newvalue):
        self.newvalue=newvalue         
    def pitchmappingGSR(self,oldfactor):
        minfactor=0 
        newfactor = oldfactor+(self.newvalue-oldfactor)*2        
        if newfactor<minfactor:
#            print "GSR pitch factor = ", minfactor
            return minfactor
        else:
#            print "GSR pitch factor = ", newfactor
            return newfactor

    def pitchmappingECG(self,oldfactor):
        minfactor=-5
        maxfactor=5
        newfactor = np.round(self.newvalue+oldfactor,2)
        if newfactor<minfactor:
#            print "ECG pitch factor = ", minfactor
            return minfactor
        if newfactor>maxfactor:
#            print "ECG pitch factor = ", maxfactor
            return maxfactor
        else:
#            print "ECG pitch factor = ", newfactor
            return newfactor
        
    def volmapping(self,oldfactor):
        #might need to change these factors when I we do more testing
        #max postive deviation
        if (self.newvalue>=10.0):
            newfactor=94 
        #max negative deviation
        if (self.newvalue<=-10.0):
            newfactor=12 
       #5-10% deviation
        if (self.newvalue>=5.0 and self.newvalue<10.0):
            newfactor=88 #77
        elif (self.newvalue>=-10.0 and self.newvalue<-5.0):
            newfactor=36 #26
        #1-4% deviation
        elif (self.newvalue>=1 and self.newvalue<4.9):
            newfactor=80 #72
        elif (self.newvalue>=-4.9 and self.newvalue<-1.0):
            newfactor=42 #36          
         #0.5-1% deviation
        elif (self.newvalue>=0.5 and self.newvalue<0.9):
            newfactor=77 #59
        elif (self.newvalue>=-0.9 and self.newvalue<-0.5):
            newfactor=51 #42
        else:
            newfactor=51 #51
        
        factor=abs(newfactor+(newfactor-oldfactor))
        volfactor= np.round(14.322*np.log(factor)-66.227)
#        print "vol factor: ",volfactor, 'new vol:',newfactor,'old vol:',oldfactor
        if volfactor>=-1:
            return -1,94
        if volfactor<=-30:
            return -30,12
        return volfactor,oldfactor
        
    def tempomapping(self, oldfactor): 
        minfactor = 0.8
        maxfactor = 1.5
        newfactor = np.round(self.newvalue,2)+oldfactor
        if newfactor<minfactor:
#            print "tempo factor = ", minfactor
            return minfactor
        elif newfactor > maxfactor:
#            print "tempo factor = ", maxfactor
            return maxfactor
        else:
#            print "tempo factor = ", newfactor
            return newfactor



##------------MAIN--------------------#
#if __name__=='__main__':
#    import time
#    mcf = music_calibration('piano.wav', 10)
#    flute,Fs = mcf.music_cali()
#    flute_stream = mcf.create_stream()
#    for i in range(0,3):
#        snd = flute.popleft()
#        fft=np.fft.fft(snd)
#        print len(fft)
#        f = np.linspace(-Fs/2, Fs/2, num=len(fft))
##        for i in (-Fs/2,Fs/2,1/len(fft)):
##            f.append(i)
#        print len(f)
#        plt.figure(1)
#        plt.plot(f,abs(np.fft.fftshift(fft)))
#        
#        if i==1:
#            start_time=time.time()
#            m = music(snd, Fs)
#            data = m.pitchshifter(-5)
#            print 'shift down', time.time()-start_time
#            
#        elif i==2:
#            start_time=time.time()            
#            m = music(snd, Fs)
#            data = m.pitchshifter(5)
#            print 'shift up', time.time()-start_time
#        else:
#            data = snd
#        flute_stream.write(data.tobytes())
#        flute.append(snd)