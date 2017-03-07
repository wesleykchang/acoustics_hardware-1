import scpi
import sys
from json import dumps
from time import sleep
import signal
import matplotlib.pyplot as plt


class RedPitaya():
    """
    A (currently aquisition-only) lib for the Red Pitaya.

    List of commands and args (with their API calls) can be found here:
    http://www.alldaq.com/fileadmin/user_upload/files/datasheets/
    redpitaya/Red_Pitaya_SCPI_commands_beta_release.pdf 

    Detailed API info can be found by cross-referencing that list with
    the <rp.h> file, which can be found with convenient links here:
    http://libdoc.redpitaya.com/rp_8h.html
    """

    def __init__(self, url,port=5000,timeout=1):
        self.rp = scpi.scpi(url,port=port,timeout=timeout)
        self.reset() #for good luck?
        signal.signal(signal.SIGINT,  self.cleanup)
        signal.signal(signal.SIGQUIT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
    
    def cleanup(self,*args):
        print("closing SCPI connection...")
        self.rp.close()

    def write(self,msg):
        self.rp.tx_txt(bytes(msg,"UTF-8"))

    def read(self):
        try:
            return self.rp.rx_txt()
        except InterruptedError: #this fires if we SIGTERM
            return 

    def reset(self):
        """Turns off acquisition and resets all ACQ params
        to their Pitaya-given defaults."""
        self.write("ACQ:RST")
        self.write("ACQ:TRIG:LEV 200 mV")
        self.write("GEN:RST")

    def _set_trig_mode(self,mode,noread=False):
        """
        mode should be one of:
          "CH2_PE" - positive edge reading from IN2
          "EXT_PE" - positive edge reading from the digital IO pin.
        There are other options (see api docs) but for now I think
        these are the only ones we should be using. Maybe remove
        this once we settle in on which trigger mode we like most?
        """
        self.write("ACQ:TRIG {}".format(mode))

    def _trigger_status(self):
        """Returns "TR" if triggered (or trigger disabled)
        and "WAIT" if it's waiting for a triggering event"""
        #return self.write("ACQ:TRIG:STAT?")
        self.write("ACQ:TRIG:STAT?")
        return self.read()

    def trigger_now(self):
        self.write("ACQ:TRIG NOW")

    def prime_trigger(self):
        self.write("ACQ:START") #reset/prime acquisition and trigger
        self.write("ACQ:TRIG CH2_PE")
        self.write("ACQ:TRIG:DLY 8192") #puts trigger event at far left of sample range

    def get_waveform(self,delay=0,time=0, wait_for_trigger=True, return_trigger=False):
        """
        If this hangs while testing, try setting wait_for_trigger to False.

        The maximum sampling rate of the Pitaya is 125MHz (8ns resolution).
        By default, it is set to that. The buffer len is 16385. This means 
        the range is 134us and will stay that way unless we lower the
        sampling rate (stupid) or truncate the buffer (in post-processing or
        by only accessing part of the buffer).

        If return_trigger=True, a second value will be returned (ie. `return data1,data2`) 
        where the second return value is the acquired trigger with the same delay/timing
        as the normal data.
        """

        while wait_for_trigger and self._trigger_status()!="TD".encode("UTF-8"):
            sleep(0.01)
            continue
        self.write("ACQ:SOUR1:DATA?")
        wave = self.read()
        data = self._parse_acq(wave)
        if return_trigger:
            self.write("ACQ:SOUR2:DATA?")
            wave2 = self.read()
            data2 = self._parse_acq(wave2)
            return self._clip_waveform(data,delay,time), self._clip_waveform(data2,delay,time)
        else:
            return self._clip_waveform(data,delay,time)

    def _clip_waveform(self,data,delay,time):
        """Takes a wave ( [[<times>],[]] ) and clips it given
        the delay and time. Time indicates the total length of the returned
        waveform, and delay is how long after the trigger even the desired
        range begins.
        
        This may be better to implement in hardware, but for now we'll
        do it here."""

        new_waves = []
        new_times = []
        for i in range(len(data[0])):
            t = data[0][i]
            if t < delay:
                continue
            elif time>0 and t > delay + time:
                break
            wave = data[1][i]
            new_waves.append(wave)
            new_times.append(t)
        return [new_times,new_waves]

    def _parse_acq(self,acq,timestep=8,delay=0):
        """Takes acq, which should be a string like "{0.1,0.34..}" from
        the pitaya, and converts it to a [times,waveform] list. times
        are computed using timestep and delay. timestep defaults to the
        pitaya's max sample rate (8ns) and delay defaults to 0."""
        acq = str(acq) #convert from bytes
        start = acq.find("{")
        end = acq.find("}")
        if start==-1 or end==-1:
            error = ValueError("Bad waveform string")
            raise(error)
        raw = "".join([x for x in acq[start:end+1] if ['{','}'].count(x)==0])
        amp = [float(x) for x in raw.split(",")] #let this fail if bad data?
        times = [((x*timestep)+delay)/1000.0 for x in range(len(amp))]
        return [times,amp]

    def ricker(self,f):
        """generate a ricker to be output by RP. max is 16k values"""
        duration = 4*np.sqrt(6)/(np.pi*f)
        ts = np.linspace(-duration/2,duration/2,16000)
        ys = (1.0 - 2.0*(np.pi**2)*(f**2) *(ts**2))*np.exp(-(np.pi**2)*(f**2)*(ts**2))
        return ys, duration


    def gen_pulse(self):
        """Function to test the signal generator on the red pitaya""" 
        self.write("SOUR1:FREQ:FIX  2250")
        self.write("SOUR1:FUNC SQUARE")
        self.write("SOUR1:VOLT 1")
        self.write("OUTPUT1:STATE ON")

    def gen_ricker(self,f):
        #add burst, arbitrary signal gen
        data,duration = self.ricker(f)
        array = str(data)[1:-1]
        self.write("SOUR1:FUNC ARBITRARY")
        self.write("SOUR1:TRAC:DATA:DATA %s" % array) 
        self.write("SOUR1:BURS:NOR INF") #inf just for testing purposes. will change this to 1
        self.write("SOUR1:BURS:PER %f" % (duration*1e6)) #period is in us
        self.write("SOUR1:BURS:STAT ON")
        # self.write("SOUR1:TRIG:SOUR INT") #internal trigger
        self.write("OUTPUT1:STATE ON")


    # def custom_pulse(self,data):
    #     #add burst, arbitrary signal gen
    #     array = str(data)[1:-1]
    #     self.write("SOUR1:TRAC:DATA:DATA %s" % array) 





if __name__=="__main__":
    r = RedPitaya("169.254.1.10")
    r.gen_pulse()
    sleep(10)
    r.rp.close()
    # data = r.get_waveform(delay=5,time=10,wait_for_trigger=True)
    # # plt = plt.plot()
    # plt.plot(data[0],data[1])
    # plt.show()

        
