# Built on example from official DSK python wrapper library

import ctypes
import json
import time

from picosdk.ps4000 import ps4000 as ps
from picosdk.functions import adc2mV, assert_pico_ok

import utils

chandle = ctypes.c_int16()


class Picoscope():
    """
    
    Attributes:
        channel (str): Optional. The physical channel, either A or B.
            Defaults to 'B'
    """

    def __init__(self):#, preTriggerSamples: int = 2500, postTriggerSamples: int = 2500):

        # self.maxSamples = preTriggerSamples + postTriggerSamples

        self.ps = None
        self.status = dict()

    def set_input_channel(self, params: dict):
        """Sets the physical input channel, either A or B.
        
        Args:
            params (dict): All sweep parameters. See settings for further info
        """

        if not params.has_key('channel'):
            params['channel'] = 'B'

        self.channel = params['channel']

    def connect(self):
        """Connects to oscilloscope."""

        if not self.ps:
            self.ps = ps

        self.status["openunit"] = self.ps.ps4000OpenUnit(ctypes.byref(chandle))

        assert_pico_ok(self.status["openunit"])

    def setSigGenBuiltInSimple(self, **nondefault_params):
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

        with open("settings.json") as f:
            settings = json.load(f)
        sigGenBuiltIn = settings["sigGenBuiltIn"]

        # Use nondefault params
        for parameter, value in nondefault_params.items():
            sigGenBuiltIn[parameter] = value
        
        self.status["SigGen"] = self.ps.ps4000SetSigGenBuiltIn(
            ctypes.byref(chandle),
            sigGenBuiltIn.offsetVoltage,
            sigGenBuiltIn.pkToPk,
            sigGenBuiltIn.waveType,
            sigGenBuiltIn.start_freq,
            sigGenBuiltIn.end_freq,
            sigGenBuiltIn.increment,
            sigGenBuiltIn.dwell,
            sigGenBuiltIn.sweepType,
            sigGenBuiltIn.operationType,
            sigGenBuiltIn.shots,
            sigGenBuiltIn.sweeps,
            sigGenBuiltIn.triggerType,
            sigGenBuiltIn.triggerSource,
            None
        )

        assert_pico_ok(self.status["SigGen"])

    def setChannel(self, voltage_range: dict):
        """Sets various channel parameters.
        
        Args:
            voltage_range (int): Optional. Specifies measuring voltage range [V].
                Refer to programmers' manual for further info.
                Note that I have modified this parameter slightly from the SDK.
                Defaults to 5 [V]
        """

        channel = f"PS4000_CHANNEL_{self.channel}"

        if not voltage_range.has_key('voltage'):
            voltage_range['voltage'] = 5.0

        parsed_voltage_range = utils.parse_voltage_range(
            numerical_voltage_range=voltage_range['voltage']
        )

        self.status["setCh"] = self.ps.ps4000SetChannel(
            chandle,
            channel,
            True,
            True,
            parsed_voltage_range
        )

        assert_pico_ok(self.status["setCh"])

    def get_timebase(self, timebase: int = 0):
        # Get timebase information
        # Warning: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.  
        # To access these Timebases, set any unused analogue channels to off.
        # handle = chandle
        # timebase = 8 = timebase
        # noSamples = maxSamples
        # pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
        # pointer to maxSamples = ctypes.byref(returnedMaxSamples)
        # segment index = 0

        timeIntervalns=ctypes.c_float()
        returnedMaxSamples = ctypes.c_int32()

        self.status["getTimebase2"] = self.ps.ps4000GetTimebase2(
            chandle,
            timebase,
            self.maxSamples,
            ctypes.byref(timeIntervalns),
            ctypes.c_int16(1),
            ctypes.byref(returnedMaxSamples),
            0
        )
            
        assert_pico_ok(self.status["getTimebase2"])

    def setSimpleTrigger(self, threshold: float = -0.01, direction: str = 'Falling', delay: float = 0.0):
        """Arms the trigger.
        
        Args:

                
        """

        autoTrigger_ms = 100

        self.status["SimpleTrigger"] = self.ps.ps4000SetSimpleTrigger(
            ctypes.byref(chandle),
            1,
            self.channel,
            threshold,
            delay,
            autoTrigger_ms
        )

        assert_pico_ok(self.status["SimpleTrigger"])

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

    def wait_ready(self):
        """Waits for data collection to finish"""

        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        while ready.value == check.value:
            self.status["isReady"] = self.ps.ps4000IsReady(chandle, ctypes.byref(ready))

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
        maxADC = ctypes.c_int16(32767)
        adc2mVChAMax =  adc2mV(bufferMax, chRange, maxADC)

        return adc2mVChAMax

    def sweep(self, params: dict):
        '''Wrapper for frequency sweep.

        params (dict): All sweep parameters. See settings for further info

        '''

        # ps.set_averaging(0)

        # ps.set_sample_rate(10*params['end_freq'])
        # sample_rate = utils.set_sample_rate(
        #     xx,
        #     end_freq=params['end_freq']
        # )

        self.set_input_channel(params=params)
        self.connect()
        self.setSigGenBuiltInSimple(params=params)

        self.setChannel(voltage_range=params)
        self.get_timebase()
        self.setSimpleTrigger()
        self.runBlock()
        self.wait_ready()
        data = self.getData(self.nsamples)

        time.sleep(0.05)

        return data.tolist()