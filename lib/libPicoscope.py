import numpy as np
import time
from picoscope import ps2000a
import matplotlib.pyplot as plt
import libCompactPR as cp
import ctypes

class Picoscope():
    """
    An acquisition library for the Picoscope 2208B.

    List of commands and args (with their API calls) can be found here:
    uses the picoscope python package and drivers from the picoscope website

    Control is acheived by using standard SCPI calls over USBTMC python library
    """

    def __init__(self, avg_num=32):
        self.ps = None
        self.avg_num = avg_num
        self.AWG_max_samples = 32768

        
        # self.sample_rate = 5e8  # sampe rate in stamples/sec
        # self.maxV = 0.2
        # self.duration = 30e-6
        # self.ps = ps2000a.PS2000a()
        # self.sample_rate, self.nsamples, self.maxsamples = self.ps.setSamplingInterval(1/self.sample_rate, self.duration)
        # self.sample_rate = 1/self.sample_rate

        # self.avg_num = avg_num
        # self.ps.memorySegments(avg_num)
        # self.ps.setNoOfCaptures(avg_num)
        
        # self.maxV = self.ps.setChannel('A', 'DC', self.maxV, 0.0, enabled=True, BWLimited=False)
        # self.ps.setSimpleTrigger('B', 0.5, 'Rising', timeout_ms=10000, enabled=True)

    def connect(self):
        if not self.ps:
            self.sample_rate = 5e8  # sampe rate in stamples/sec
            self.maxV = 0.5
            self.duration = 30e-6
            self.ps = ps2000a.PS2000a()
            self.sample_rate, self.nsamples, self.maxsamples = self.ps.setSamplingInterval(1/self.sample_rate, self.duration)
            self.sample_rate = 1/self.sample_rate

            self.ps.memorySegments(self.avg_num)
            self.ps.setNoOfCaptures(self.avg_num)
                
    def cleanup(self, *args):
        self.ps.stop()
        self.ps.close()

    def read(self, delay, duration):
        try:
            waves = []
            for i in range(0, self.avg_num):
                waves.append(self.ps.getDataV('A', self.nsamples, returnOverflow=False, segmentIndex=i))            
            return waves
        except KeyboardInterrupt: #this fires if we SIGTERM
            return
        
    def set_maxV(self,  maxV, channel=1):
        self.connect()
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
        for opt in options:
            if maxV <= opt+0.005:
                break
        self.maxV = opt
        return
    
    def get_maxV(self, channel=1):
        '''
        gets the maximum voltage for the given channel in V
        '''
        return self.maxV
    
    def reset(self):
        """
        Resets system to init settings
        """
        self.__init__()
        
    def trigger_now(self):
        '''
        instantly triggers the system
        '''
        return
    
    def prime_trigger(self, delay=0, duration=20.0):
        '''
        readies the trigger for waveform collection
        '''
        self.connect()
        self.sample_rate, self.nsamples, self.maxsamples = self.ps.setSamplingInterval(1/self.sample_rate, duration*1e-6)
        self.sample_rate = 1/self.sample_rate
        
        self.maxV = self.ps.setChannel('A', 'DC', self.maxV, 0.0, enabled=True, BWLimited=False)
        self.ps.setSimpleTrigger('B', 0.5, 'Rising', timeout_ms=10000, delay=int(delay*1e-6*self.sample_rate), enabled=True)

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
        
    def get_waveform(self, delay=1.5, duration=20, pct_diff_avg_cutoff=0.1, wait_for_trigger=True, return_waves=False):
        """
        If this hangs while testing, try setting wait_for_trigger to False.

        The maximum sampling rate of the scope is 500MHz (2ns resolution).
        By default, it is set to that. The buffer len is 20480
        """
        if wait_for_trigger:
            self.ps.waitReady()
        waves = self.read(delay, duration)
        
        amp_sum = list(map(np.sum, map(abs, waves)))
        m = np.mean(amp_sum)
        amp_sum_pct = np.abs(np.divide(np.subtract(amp_sum, m), m))
        waves_avg = np.array(waves)[amp_sum_pct < pct_diff_avg_cutoff]
        
        data = np.mean(np.transpose(waves_avg), axis=1).tolist()
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
        
        self.connect()
        self.ps.setSigGenBuiltInSimple(offsetVoltage=offset, pkToPk=pkToPk, waveType=waveType, frequency=frequency,
                                       shots=shots, triggerSource='SoftTrig', stopFreq=stopFreq, increment=increment,
                                       numSweeps=numSweeps, dwellTime=dwellTime, sweepType='Up')

        self.sample_rate = 1e6
        self.sample_rate, self.nsamples, self.maxsamples = self.ps.setSamplingInterval(1/self.sample_rate, 10)
        self.sample_rate = 1/self.sample_rate
        
        self.maxV = self.ps.setChannel('B', 'DC', 2, 0.0, enabled=True, BWLimited=False)
        self.ps.setSimpleTrigger('B', -0.1, 'Falling', timeout_ms=200, delay=0, enabled=True)
        
        self.ps.runBlock()
        self.trig_AWG()
        self.wait_ready()

        data = self.ps.getDataV('B', self.nsamples, returnOverflow=False)
        t = np.arange(0,len(data)) * 1/self.sample_rate
        plt.plot(t, data)
        plt.show()
        
    def generate_waveform(self, waveform, duration, dual=False, npulses=1):
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
        
if __name__=="__main__":
    # cp = cp.CP("http://localhost:9003",rp_url="169.254.1.10")
    ps = Picoscope(avg_num=0)
    # ps.generate_square(voltage=-2.0)
    ps.signal_generator(stopFreq=1000, frequency=100, shots=0, numSweeps=1, increment=100, dwellTime=0.5)
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
