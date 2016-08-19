import scpi
import sys
from json import dumps
from time import sleep

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

    def write(self,msg):
        self.rp.tx_txt(bytes(msg,"UTF-8"))

    def read(self):
        return self.rp.rx_txt()

    def reset(self):
        """Turns off acquisition and resets all ACQ params
        to their Pitaya-given defaults."""
        self.write("ACQ:RST")
        self._set_trig_mode("CH2_PE")
        self.write("ACQ:START")

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

    def get_waveform(self,channel=1,wait_for_trigger=True):
        """
        If this hangs while testing, try setting wait_for_trigger to False.

        The maximum sampling rate of the Pitaya is 125MHz (8ns resolution).
        By default, it is set to that. The buffer len is 16385. This means 
        the range is 134us and will stay that way unless we lower the
        sampling rate (stupid) or truncate the buffer (in post-processing or
        by only accessing part of the buffer).
        """
        if [1,2].count(channel)==0:
            error = ValueError("Channel must be an integer, either 1 or 2")
            raise(error)

        while wait_for_trigger and self._trigger_status()!="TR":
            sleep(0.01)
            continue
        self.write("ACQ:SOUR{}:DATA?".format(channel))
        wave = self.read()
        return self._parse_acq(wave)

    def _parse_acq(self,acq,timestep=8,delay=0):
        """Takes acq, which should be a string like "{0.1,0.34..}" from
        the pitaya, and converts it to a [times,waveform] list. times
        are computed using timestep and delay. timestep defaults to the
        pitaya's max sample rate (8ns) and delay defaults to 0."""
        acq = str(acq) #convert from bytes
        start = acq.find("{")
        end = acq.find("}")
        print(start)
        print(end)
        if start==-1 or end==-1:
            error = ValueError("Bad waveform string")
            raise(error)
        raw = "".join([x for x in acq[start:end+1] if ['{','}'].count(x)==0])
        amp = [float(x) for x in raw.split(",")] #let this fail if bad data?
        times = [(x*timestep)+delay for x in range(len(amp))]
        return [times,amp]


if __name__=="__main__":
    r = RedPitaya("169.254.134.177")
    r.trigger_now()
    print(r.get_waveform(wait_for_trigger=False))
        
