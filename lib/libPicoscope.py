import numpy as np
import time
from picoscope import ps4000
import libCompactPR as cp
import ctypes


try:
    import matplotlib.pyplot as plt
    graphical = True
except (TypeError,ImportError):
    graphical = False

class Picoscope():
    """
    An acquisition library for the Picoscope 4262.

    List of commands and args (with their API calls) can be found here:
    https://github.com/colinoflynn/pico-python

    Uses a 3rd party python wrapper for official C driver functions
    """

    options = [
        0.02,
        0.05,
        0.1,
        0.2,
        0.5,
        1.0,
        2.0,
        5.0,
        10.0,
        20.0
    ]

    AWG_max_samples = 32768
    scope_max_samples = 128e6
    
    def __init__(self, avg_num=32, duration=30e-6, sample_rate=5e8,resonance=False, maxV = .2):
        '''
        creates picoscope object, but doesn't actually connect to instrumenet
        CALL connect() TO ACTUALLY INITIATE CONNECTION
        '''
        self.ps = None
        self.avg_num = avg_num
        
        self.sample_rate = sample_rate  # samples/sec
        self.vrange = maxV  # clipping voltage
        self.duration = duration  # capture duration in seconds

    def connect(self):
        '''
        connects to the picoscope, sets up defaults, must be called separately to init.
        will fail weirdly if called before process daemon-ization
        '''
        if not self.ps:
            self.ps = ps4000.PS4000()

            self.set_averaging(self.avg_num)
            self.sample_rate, self.nsamples, self.maxsamples = self.ps.setSamplingInterval(1/self.sample_rate, self.duration)
            self.sample_rate = 1/self.sample_rate

    def set_averaging(self, num):
        '''
        set waveform averaging count
        '''
        self.ps.memorySegments(num)
        self.ps.setNoOfCaptures(num)
        self.avg_num = num

    def set_sample_rate(self, rate):
        '''
        set sampling rate in samples/sec
        '''
        self.sample_rate = rate
        
    def cleanup(self, *args):
        '''
        closes connections and such
        '''
        self.ps.stop()
        self.ps.close()

    def read(self):
        '''
        pulls waves off of a completed picoscope run
        '''
        try:
            #waves = []
            #for i in range(0, self.avg_num):
            #    waves.append(self.ps.getDataV('A', self.nsamples, returnOverflow=False, segmentIndex=i))
            #return waves

            #waves = []
            #for i in range(0, self.averaging):
            #    waves.append(self.ps.getDataV(self.rs['_data_channel'], self.nsamples, returnOverflow=False, segmentIndex=i))
            #print(time.time() - t)
            #return waves

            data = np.ascontiguousarray(np.zeros((self.avg_num, self.nsamples), dtype=np.int16))
            ch = self.ps.CHANNELS['A']
            for i, segment in enumerate(range(0, self.avg_num)):
                self.ps._lowLevelSetDataBuffer(ch,data[i],0, segment)

            overflow = np.ascontiguousarray(np.zeros(self.avg_num, dtype=np.int16))
            self.ps._lowLevelGetValuesBulk(self.nsamples, 0, self.avg_num-1,1, 0, overflow)

            # don't leave the API thinking these can be written to later
            for i, segment in enumerate(range(0, self.avg_num)):
                self.ps._lowLevelClearDataBuffer(ch, segment)

            waves = []
            for wave in data:
                waves.append(self.ps.rawToV('A', wave))
            return waves

            
        except KeyboardInterrupt: #this fires if we SIGTERM
            return

    def auto_range(self, delay=0.0, duration=20.0):
        '''
        takes one waveform and sets the optimal range based on that
        requires the pulser to be running
        '''
        
        avg_num = self.avg_num
        
        #disable averaging
        self.set_averaging(1)

        #do auto ranging from 1V start
        self.vrange = 1.0
        self.prime_trigger(delay, duration)
        t,data = self.get_waveform()
        
        ma = np.max(data)
        mi = np.abs(np.min(data))
        if mi > ma:
            ma = mi

        #figure out if it needs 5V or 2V if >1V on first pass    
        if ma >= 0.95:
            self.vrange = 2.0
            self.prime_trigger(delay, duration)
            t,data = self.get_waveform()
            ma = np.max(data)
            mi = np.abs(np.min(data))
            if mi > ma:
                ma = mi
            if ma >= 1.95:
                self.set_maxV(5.0)
            else:
                self.set_maxV(2.0)

        #just set maxV if there was no clipping
        else:
            self.set_maxV(ma+0.005)

        #reset averaging
        self.set_averaging(avg_num)

    def set_maxV(self,  maxV, offset=0.0, channel=1):
        '''
        set the clipping voltage
        '''
        for opt in Picoscope.options:
            if maxV <= opt+0.000001:
                break
        self.vrange = opt
        return
    
    def get_maxV(self, channel=1):
        '''
        gets the maximum voltage for the given channel in V
        '''
        return self.vrange
    
    def reset(self):
        """
        Resets system to init settings
        """
        self.__init__()
        self.ps = None
        self.connect()
        
    def prime_trigger(self, delay=0, duration=20.0, timeout_ms=1000):
        '''
        readies the trigger for waveform collection
        '''
        self.sample_rate, self.nsamples, self.maxsamples = self.ps.setSamplingInterval(1/self.sample_rate, duration*1e-6)
        self.sample_rate = 1/self.sample_rate
        
        self.vrange = self.ps.setChannel('A', 'DC', self.vrange, 0.0, enabled=True, BWLimited=False)
        self.ps.setSimpleTrigger('B', 0.5, 'Rising', timeout_ms=timeout_ms, delay=int(delay*1e-6*self.sample_rate), enabled=True)

        self.ps.runBlock()
        
    def stop_acq(self):
        '''
        stops acquisition
        '''
        self.ps.stop()

    def wait_ready(self):
        '''
        waits for picoscope to finish acquisition
        '''
        self.ps.waitReady()
        
    def get_waveform(self, pct_diff_avg_cutoff=0.1, wait_for_trigger=True, return_waves=False):
        """
        The maximum sampling rate of the scope is 500MHz (2ns resolution).
        By default, it is set to that.
        Discards waves whose amp-sum is pct_diff_avg_cutoff away from mean
        """
        if wait_for_trigger:
            self.ps.waitReady()
        waves = self.read()
        
        #amp_sum = list(map(np.sum, map(abs, waves)))
        #m = np.mean(amp_sum)
        #amp_sum_pct = np.abs(np.divide(np.subtract(amp_sum, m), m))
        #waves_avg = np.array(waves)[amp_sum_pct < pct_diff_avg_cutoff]
        
        data = np.mean(np.transpose(waves), axis=1).tolist()
        t = np.arange(self.nsamples) * (1/self.sample_rate)*1e6
        t = t.tolist()
        if return_waves:
            return waves
        else:
            return [t, data]

    def trig_AWG(self):
        '''
        starts the arbitrary wave generator. must prime scope trigger before calling
        '''
        self.ps.lib.ps2000aSigGenSoftwareControl(ctypes.c_int16(self.ps.handle), ctypes.c_int(0))

    def generate_square(self, pwidth=444e-9, voltage=-2.0):
        '''
        generates a square pulse at the specified width with specified voltage
        '''
        if voltage < -2.0:
            voltage = -2.0
        elif voltage > 2.0:
            voltage = 2.0
        
        pulse = np.add(np.zeros(10), voltage)
        zero = np.zeros(10)
        wf = np.append(pulse, zero)
        
        self.generate_waveform(wf, pwidth*2)

    def signal_generator(self, offset=0.0, waveType='Sine', pkToPk=2, frequency=1.0e6, stopFreq=None,
                         increment=10.0, shots=10, dwellTime=0.001, numSweeps=0):
        '''
        generates a signal.
        waveTypes are:
        'Sine'
        'Square'
        'Triangle'
        'RampUp'
        'RampDown'
        'DCVoltage'
        '''
        
        if stopFreq != None:
            if stopFreq > self.sample_rate*2:
                print("warning: sample rate is less than Nyquist frequency!")

        self.connect()
        self.ps.setSigGenBuiltInSimple(offsetVoltage=offset, pkToPk=pkToPk, waveType=waveType, frequency=frequency,
                                       shots=shots, triggerSource='SoftTrig', stopFreq=stopFreq, increment=increment,
                                       numSweeps=numSweeps, dwellTime=dwellTime, sweepType='Up')

        duration = dwellTime*((stopFreq - frequency)/increment + 1)
        self.sample_rate, self.nsamples, self.maxsamples = self.ps.setSamplingInterval(1/self.sample_rate, duration)
        self.sample_rate = 1/self.sample_rate

        self.vrange = self.ps.setChannel('B', 'DC', self.vrange, 0.0, enabled=True, BWLimited=False)
        self.ps.setSimpleTrigger('A', 1.0, 'Falling', timeout_ms=1, delay=0, enabled=True)
        
        #self.ps.runBlock(pretrig=0.5)

        self.ps.runBlock(pretrig=0.001/duration)
        self.trig_AWG()

        self.wait_ready()

        data = self.ps.getDataV('B', self.nsamples, returnOverflow=False)
        t = np.arange(0,len(data)) * 1/self.sample_rate
        
        t = t.tolist()
        data = data.tolist()

        self.ps.setSigGenBuiltInSimple(waveType='DCVoltage', offsetVoltage=0, shots=0)
        self.trig_AWG()
        time.sleep(0.05)

        # plt.plot(t, data)
        # plt.show()
        return [t,data]

        
    def generate_waveform(self, waveform, duration, rx_samplerate, dual=False, npulses=1):
        '''
        generates an arbitrary waveform given by the Voltage amplitude values in waveform
        the length of the waveform array has a max of 32768
        duration is the time duration that this waveform will be spread over
        waveform is in volts. Max voltage is +- 2V
        Voltage does not return to zero automatically and will stay at the last setting
        '''
        self.connect()

        npulses = npulses+1
        duration = duration / 5
        
        if dual:
            indexMode = 'Dual'
        else:
            indexMode = 'Single'

        maxV = max(waveform)
        minV = min(waveform)
        pkToPk = maxV - minV
        offset = (maxV - abs(minV))/2
        
        waveform = np.divide(np.subtract(waveform, minV), pkToPk) #scale to 1:0
        waveform = np.multiply(np.subtract(waveform, 0.5), 2.0) #scale to 1:-1
        waveform = np.array(np.multiply(waveform, 32767), dtype=np.int16) #scale to 32767:-32767

        
        self.ps.setAWGSimple(waveform, duration, pkToPk=pkToPk, offsetVoltage=offset,
                             triggerSource='SoftTrig', indexMode=indexMode, shots=npulses)



        #change the sample_rate on the receive side.
        self.sample_rate, self.nsamples, self.maxsamples = self.ps.setSamplingInterval(1/rx_samplerate, duration*5)
        self.sample_rate = 1/rx_samplerate


        self.vrange = self.ps.setChannel('B', 'DC', self.vrange, 0.0, enabled=True, BWLimited=False)
        self.ps.setSimpleTrigger('B', -0.01, 'Falling', timeout_ms=1, delay=0, enabled=True)
        self.ps.runBlock()
        self.trig_AWG()
        self.wait_ready()
        data = self.ps.getDataV('B', self.nsamples, returnOverflow=False)
        t = np.arange(0,len(data)) * 1/self.sample_rate
        t.tolist()
        # plt.plot(t, data)
        # plt.show()
        return [t,data]
        
if __name__=="__main__":
    ps = Picoscope(avg_num=64)
    ps.connect()
    ps.prime_trigger(timeout_ms=1)
    data = ps.get_waveform()

    t = time.time()
    ps.set_sample_rate(5e8)
    ps.prime_trigger(timeout_ms=1, duration=120)
    data = ps.get_waveform()
    print(time.time() - t)


    # cp = cp.CP("http://localhost:9003",rp_url="169.254.1.10")
    # ps = Picoscope(avg_num=0)
    # ps.generate_square(voltage=-2.0)
    # ps.signal_generator(stopFreq=1000, frequency=100, shots=0, numSweeps=1, increment=100, dwellTime=0.5)
    # x = np.add(np.zeros(16384, dtype=np.int16), -2)
    # y = np.add(np.zeros(16384, dtype=np.int16), 0)
    
    # arr = np.append(x,y)
    # t, data = ps.generate_waveform(arr, 50e-6)
    
    # plt.plot(t, data)
    # plt.show()
    
    
    # cp.write('V100')
    # cp.write('V?')
    # print(cp.read())
    # ps.prime_trigger()
    # cp.write('P50')
    # data = ps.get_waveform(return_waves=True)
    # cp.write('P0')
    # for wave in data:
    #     plt.plot(wave)
    # plt.show()

    # cp.write('V300')
    # cp.write('V?')
    # print(cp.read())
    # ps.prime_trigger()
    # cp.write('P50')
    # data = ps.get_waveform(return_waves=True)

    # cp.write('P0')
    # for wave in data:
    #     plt.plot(wave)
    # plt.show()
