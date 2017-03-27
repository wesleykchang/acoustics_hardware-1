import numpy as np
import time
from picoscope import ps2000a

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
            self.maxV = 0.2
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
        
        self.ps.memorySegments(self.avg_num)
        self.ps.setNoOfCaptures(self.avg_num)

        self.maxV = self.ps.setChannel('A', 'DC', self.maxV, 0.0, enabled=True, BWLimited=False)
        self.ps.setSimpleTrigger('B', 0.5, 'Rising', timeout_ms=10000, delay=int(delay*1e-6*self.sample_rate), enabled=True)

        self.ps.runBlock(segmentIndex=0)
    
    def stop_acq(self):
        '''
        stops acquisition
        '''
        self.ps.stop()
        
    def get_waveform(self, delay=1.5, duration=20, wait_for_trigger=True):
        """
        If this hangs while testing, try setting wait_for_trigger to False.

        The maximum sampling rate of the scope is 500MHz (2ns resolution).
        By default, it is set to that. The buffer len is 20480. This means 
        the range is 40.960us and will stay that way unless we lower the
        sampling rate or truncate the buffer (in post-processing or
        by only accessing part of the buffer).
        """
        if wait_for_trigger:
            self.ps.waitReady()
        waves = self.read(delay, duration)
        data = np.mean(np.transpose(waves), axis=1).tolist()
        t = np.arange(self.nsamples) * 1/self.sample_rate
        t = t.tolist()
        
        return [t, data]
    
if __name__=="__main__":
    ps = self.Picoscope()
    # t, amp = bk.get_waveform()
    # plt.plot(t, amp)
    # plt.show()
