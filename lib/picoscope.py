# Built on example from official DSK python wrapper library

import ctypes
import json
import time

from picosdk.ps4000 import ps4000 as ps
from picosdk.functions import adc2mV, assert_pico_ok

chandle = ctypes.c_int16()

with open("settings.json") as f:
    settings = json.load(f)
sigGenBuiltIn = settings["sigGenBuiltIn"]

class Picoscope():
    def __init__(self, preTriggerSamples: int = 2500, postTriggerSamples: int = 2500):

        self.maxSamples = preTriggerSamples + postTriggerSamples

        self.ps = None
        self.status = dict()

    def connect(self):
        if not self.ps:
            self.ps = ps

        self.status["openunit"] = self.ps.ps4000OpenUnit(ctypes.byref(chandle))

        assert_pico_ok(self.status["openunit"])

    def setSigGenBuiltIn(self, **nondefault_params):
        """Sets up the signal generator to produce a signal from the selected waveType.

        If startFrequency != stopFrequency it will sweep.
        
        Args:
            offsetVoltage (float): Optional. The voltage offset [uV].
                Defaults to 0.0
            pkToPk (int): Optional. Peak-to-peak voltage [uV].
                Defaults to 2
            waveType (str): Optional. The type of waveform to be generated.
                Refer to programmers' guide for all available types. Defaults to 'Sine'
            startFrequency (float): Optional. Starting frequency.
                Defaults to 1.0E6
            stopFrequency (float): Optional. Stopping (or reversing) frequency (included).
                Defaults to None
            increment (float): Optional. The amount by which the frequency rises (or falls).
                Defaults to 10.0
            dwellTime (float): Optional. The time [s] between frequency changes.
                Defaults to 1E-3
            sweepType (str): Optional. Determines sweeping direction.
                Defaults to 'UP'
            operationType (str): Optional. Configures white noise generator.
                Defaults to None
            shots (str): Optional. The number of cycles of the waveform to be produced
                after a trigger event.
                Defaults to None
            sweeps (int): Optional. Number of sweep repetitions.
            Defaults to None
            triggerType (str): The type of trigger to be applied to signal generator.
                Refer to programmers' guide for all available types.
                Defaults to 'SIGGEN_RISING'
            triggerSource (str): Optional. The source that triggers the signal generator.
                Defaults to 'SIGGEN_SCOPE_TRIG'
        """

        for parameter, value in nondefault_params.items():
            sigGenBuiltIn[parameter] = value
        
        self.status["SigGen"] = self.ps.ps4000SetSigGenBuiltIn(
            chandle,
            sigGenBuiltIn.offsetVoltage,
            sigGenBuiltIn.pkToPk,
            sigGenBuiltIn.waveType,
            sigGenBuiltIn.startFrequency,
            sigGenBuiltIn.stopFrequency,
            sigGenBuiltIn.increment,
            sigGenBuiltIn.dwellTime,
            sigGenBuiltIn.sweepType,
            sigGenBuiltIn.operationType,
            sigGenBuiltIn.shots,
            sigGenBuiltIn.sweeps,
            sigGenBuiltIn.triggerType,
            sigGenBuiltIn.triggerSource,
            None
        )

        assert_pico_ok(self.status["SigGen"])

    def setSimpleTrigger(self):
        pass

    # setSamplingInterval doesn't exist

    def trig_AWG(self):
        pass
        #self.ps.lib.ps2000aSigGenSoftwareControl(ctypes.c_int16(self.ps.handle), ctypes.c_int(0))


    def wait_ready(self):

        # Check for data collection to finish using ps4000IsReady
        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        while ready.value == check.value:
            self.status["isReady"] = self.ps.ps4000IsReady(chandle, ctypes.byref(ready))


    def setChannel(self, channel: int = 0, enabled: int = 0, dc: int = 1, channel_range: int = 7):
        # Set up channel A
        # handle = chandle
        # channel = PS4000_CHANNEL_A = 0
        # enabled = 1
        # coupling type = PS4000_DC = 1
        # range = PS4000_2V = 7

        self.status["setCh"] = self.ps.ps4000SetChannel(
            chandle,
            channel,
            enabled,
            dc,
            channel_range
        )

        assert_pico_ok(self.status["setCh"])

    def setSingleTrigger(self, enabled: int = 1, source: int = 0, threshold: int = 1024, direction: int = 2, delay: int = 0, auto_trigger: int = 1000):
        # Set up single trigger
        # handle = chandle
        # enabled = 1
        # source = PS4000_CHANNEL_A = 0
        # threshold = 1024 ADC counts
        # direction = PS4000_RISING = 2
        # delay = 0 s
        # auto Trigger = 1000 ms

        self.status["trigger"] = self.ps.ps4000SetSimpleTrigger(
            chandle,
            enabled,
            source,
            threshold,
            direction,
            delay,
            auto_trigger
        )
        
        assert_pico_ok(self.status["trigger"])

    # def get_timebase(self, timebase: int = 8, timeIntervalns: ctypes.c_float() = None, returnedMaxSamples: ctypes.c_int32() = None):
    #     # Get timebase information
    #     # Warning: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.  
    #     # To access these Timebases, set any unused analogue channels to off.
    #     # handle = chandle
    #     # timebase = 8 = timebase
    #     # noSamples = maxSamples
    #     # pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
    #     # pointer to maxSamples = ctypes.byref(returnedMaxSamples)
    #     # segment index = 0

    #     if timeIntervalns is None:
    #         timeIntervalns=ctypes.c_float()

    #     if returnedMaxSamples is None:
    #         returnedMaxSamples = ctypes.c_int32()

    #     self.status["getTimebase2"] = self.ps.ps4000GetTimebase2(
    #         chandle,
    #         timebase,
    #         self.maxSamples,
    #         ctypes.byref(timeIntervalns),
    #         ctypes.c_int16(1),
    #         ctypes.byref(returnedMaxSamples),
    #         0
    #     )
            
    #     assert_pico_ok(self.status["getTimebase2"])

    def runBlock(self, timebase: int = 8, preTriggerSamples: int = 2500, postTriggerSamples: int = 2500):

        # Run block capture
        # handle = chandle
        # number of pre-trigger samples = preTriggerSamples
        # number of post-trigger samples = PostTriggerSamples
        # timebase = 8 = 80 ns = timebase (see Programmer's guide for mre information on timebases)
        # time indisposed ms = None (not needed in the example)
        # segment index = 0
        # lpReady = None (using ps4000IsReady rather than ps4000BlockReady)
        # pParameter = None
        
        self.status["runBlock"] = self.ps.ps4000RunBlock(
            chandle,
            preTriggerSamples,
            postTriggerSamples,
            timebase,
            ctypes.c_int16(1),
            None,
            0,
            None,
            None
        )

        assert_pico_ok(self.status["runBlock"])

    # def set_buffer_location(self):
    #     # Set data buffer location for data collection from channel A
    #     # handle = chandle
    #     # source = PS4000_CHANNEL_A = 0
    #     # pointer to buffer max = ctypes.byref(bufferAMax)
    #     # pointer to buffer min = ctypes.byref(bufferAMin)
    #     # buffer length = maxSamples
        
    #     bufferMax = (ctypes.c_int16 * self.maxSamples)()
    #     bufferMin = (ctypes.c_int16 * self.maxSamples)() # used for downsampling which isn't in the scope of this example

    #     self.status["setDataBuffers"] = self.ps.ps4000SetDataBuffers(
    #         chandle,
    #         0,
    #         ctypes.byref(bufferMax),
    #         ctypes.byref(bufferMin),
    #         self.maxSamples
    #     )
        
    #     assert_pico_ok(self.status["setDataBuffers"])


    def getData(self, overflow = ctypes.c_int16()):
        # Retrived data from scope to buffers assigned above
        # handle = chandle
        # start index = 0
        # pointer to number of samples = ctypes.byref(cmaxSamples)
        # downsample ratio = 0
        # downsample ratio mode = PS4000_RATIO_MODE_NONE
        # pointer to overflow = ctypes.byref(overflow))

        # create converted type maxSamples
        cmaxSamples = ctypes.c_int32(self.maxSamples)

        self.status["getValues"] = self.ps.ps4000GetValues(
            chandle,
            0,
            ctypes.byref(cmaxSamples),
            0,
            0,
            0,
            ctypes.byref(overflow)
        )

        assert_pico_ok(self.status["getValues"])

        # convert ADC counts data to mV
        chRange = 7
        adc2mVChAMax =  adc2mV(bufferMax, chRange, maxADC)

        return adc2mVChAMax

    def sweep(self, offset=0.0, waveType='Sine', pkToPk=2, frequency=1.0e6, stopFreq=None,
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
        self.setSigGenBuiltInSimple()

        duration = dwellTime*((stopFreq - frequency)/increment + 1)
        # self.sample_rate, self.nsamples, self.maxsamples = self.ps.setSamplingInterval(1/self.sample_rate, duration)
        # self.sample_rate = 1/self.sample_rate

        self.vrange = self.setChannel('B', 'DC', self.vrange, 0.0, enabled=True, BWLimited=False)
        self.ps.setSimpleTrigger('A', 1.0, 'Falling', timeout_ms=1, delay=0, enabled=True)
        
        #self.ps.runBlock(pretrig=0.5)

        self.ps.runBlock(pretrig=0.001/duration)
        self.trig_AWG()

        self.wait_ready()

        data = self.getDataV('B', self.nsamples, returnOverflow=False)
        data = data.tolist()

        self.setSigGenBuiltInSimple(waveType='DCVoltage', offsetVoltage=0, shots=0)
        self.trig_AWG()
        time.sleep(0.05)

        return data        