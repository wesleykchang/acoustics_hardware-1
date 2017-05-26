import usbtmc
import numpy as np
import time
import usb


class BKPrecision():
    """
    An acquisition library for the BK Precision 2190E Oscilliscope.

    List of commands and args (with their API calls) can be found here:
    https://bkpmedia.s3.amazonaws.com/downloads/programming_manuals/en-us/
    2190E_programming_manual.pdf   

    Control is acheived by using standard SCPI calls over USBTMC python library
    """

    def __init__(self, timeout=3):
        self.sample_rate = 5e8  # sampe rate in stamples/sec
        self.maxV = 0.5
        self.bk = usbtmc.Instrument(usbtmc.list_devices()[0])
        self.bk.timeout = timeout
        try:
            self.bk.ask('*IDN?')
        except usb.core.USBError:
            self.bk.ask('*IDN?')
        self.reset()
            
    def cleanup(self, *args):
        print("closing SCPI connection...")
        self.rp.close()

    def write_raw(self, msg):
        self.bk.write_raw(bytes(msg,"UTF-8"))

    def read_raw(self):
        try:
            return self.bk.read_raw()
        except KeyboardInterrupt: #this fires if we SIGTERM
            return
        
    def write(self, msg):
        self.bk.write(msg)

    def read(self):
        try:
            return self.bk.read()
        except KeyboardInterrupt: #this fires if we SIGTERM
            return
        
    def set_maxV(self,  maxV, channel=1):
        self.write('C{}:VOLT_DIV {}'.format(channel, maxV/5.0))
        self.maxV = maxV
        
    def get_maxV(self, channel=1):
        '''
        gets the maximum voltage for the given channel in V
        '''
        s = self.ask('C{}:VOLT_DIV?'.format(channel))
        g = s.split(' ')[1]
        g = g[:-1]
        self.maxV = float(g)*5.0
        return self.maxV
    
    def reset(self):
        """
        Resets system to acquisition settings determined by me
        """
        # self.write('*RCL 1')
        self.reset_default()
        
    def reset_default(self):
        self.write('*RST')
        self.write('C1:OFST 0')
        self.write('C2:OFST 0')
        self.set_maxV(1, channel=2)
        self.set_maxV(0.5)
        self.write('C2:TRLV 500MV')
        self.write('TRDL 20480NS')
        self.write('TIME_DIV 1NS')
        self.trigger_now()
        time.sleep(3)
        self.write('TIME_DIV 1NS')
        self.write('TRDL 20480NS')
        self.write('AVGA 256')
        self.write('*SAV 1')

    def _trigger_status(self):
        """Returns "TRMD STOP" if triggered (or trigger disabled)
        and "TRMD SINGLE" if it's waiting for a triggering event"""
        self.write('TRMD?')
        return self.read()

    def trigger_now(self):
        '''
        instantly triggers the system
        '''
        self.write('TRMD SINGLE;ARM;FRTR')

    def prime_trigger(self):
        '''
        readies the trigger for single shot data collection
        '''
        self.write('TRMD NORM')

    def stop_acq(self):
        '''
        stops acquisition
        '''
        self.write('TRMD STOP')
        
    def get_waveform(self, delay=1.5, duration=20, volt_limit=None, wait_for_trigger=True):
        """
        If this hangs while testing, try setting wait_for_trigger to False.

        The maximum sampling rate of the scope is 500MHz (2ns resolution).
        By default, it is set to that. The buffer len is 20480. This means 
        the range is 40.960us and will stay that way unless we lower the
        sampling rate or truncate the buffer (in post-processing or
        by only accessing part of the buffer).

        If return_trigger=True, a second value will be returned (ie. `return data1,data2`)
        where the second return value is the acquired trigger with the same delay/timing
        as the normal data.
        """
        if volt_limit and volt_limit != self.maxV:
            self.set_maxV(volt_limit) # sets the clipping voltage
        while wait_for_trigger and self._trigger_status() != "TRMD STOP":
            continue
        self.write('C1:WF? DAT2')
        a = self.read_raw()
        data = self._parse_acq(a) # parse raw binary data

        #clip data by delay and duration
        sample = (1/self.sample_rate)*1e6
        delay = int(delay/sample)
        duration = delay + int(duration/sample)
        if delay < 0:
            delay = 0
        if duration > len(data) - 1:
            duration = len(data) - 1
        data = data[delay:duration].tolist()

        #create time array
        t = np.arange(0, len(data))
        t = np.divide(t, self.sample_rate)
        t = np.multiply(t, 1e6).tolist()
        
        return [t, data]

    def _parse_acq(self, acq):
        '''
        parses the string of bytes outputted by the oscope
        into an array of voltages
        '''
        acq = acq.strip()
        acq = acq[21:]  # get rid of misc stuff
        amp = np.fromstring(acq, dtype=np.int8)
        amp = np.divide(amp, 128)  # convert to -1 to 1 amp
        amp = np.multiply(amp, self.maxV)
        return amp

    
if __name__=="__main__":
    bk = BKPrecision()
    # t, amp = bk.get_waveform()
    # plt.plot(t, amp)
    # plt.show()
