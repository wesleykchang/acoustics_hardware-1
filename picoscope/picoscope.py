"""Contains class Picoscope: A wrapper for the C drivers"""

import ctypes
import json
from picosdk.ps4000 import ps4000 as ps
from picosdk.functions import adc2mV, assert_pico_ok

import picoscope.utils as utils

chandle = ctypes.c_int16()


class Picoscope():
    """
    
    Attributes:
        channel (str): Optional. The physical channel, either A or B.
            Defaults to 'B'
    """

    def __init__(self):
        pass
        # self.maxSamples = preTriggerSamples + postTriggerSamples

    def _set_input_channel(self, params: dict):
        """Sets the physical input channel (either A or B).
        
        Args:
            params (dict): All sweep parameters. See settings for further info
        """

        if not 'channel' in params:
            params['channel'] = 'B'

        self.channel = params['channel']

    def connect(self):
        """Connects to oscilloscope.
        
        Note:
            There's an persistent bug where this method fails several times before a connection
            can be established. However, adding a try/except block doesn't solve it.
            The retry must be external, i.e. when running pithy/startup
        """

        status = ps.ps4000OpenUnit(ctypes.byref(chandle))

        assert_pico_ok(status)

    def _setup(self, **nondefault_params):
        """Sets up the signal generator to produce a signal from the selected waveType.

        If startFrequency != stopFrequency it will sweep.

        Note:
            All params are optional. Defaults defined in settings.json
        
        Args:
            offsetVoltage (int): The voltage offset [uV].
                Defaults to 0
            pkToPk (int): Peak-to-peak voltage [uV].
                Defaults to 2
            waveType (int): The type of waveform to be generated.
                Refer to programmers' guide for all available types. Defaults to 0 (Sine)
            startFrequency (float): Starting frequency.
                Defaults to 1.0E6
            stopFrequency (float): Stopping (or reversing) frequency (included).
                Defaults to None
            increment (float): The amount by which the frequency rises (or falls).
                Defaults to 10.0
            dwellTime (float): The time [s] between frequency changes.
                Defaults to 1E-3
            sweepType (int): Determines sweeping direction.
                Refer to programmers' guide for all available types. Defaults to 0 (UP)
            operationType (int): Configures white noise generator.
                Refer to programmers' guide for all available types.
                Defaults to 0 (white noise disabled)
            shots (0): The number of cycles of the waveform to be produced after a trigger event.
                Cannot be a nonzero value if sweeping. Defaults to 0.
            sweeps (int): Number of sweep repetitions.
                Defaults to None
            triggerType (int): The type of trigger to be applied to signal generator.
                Refer to programmers' guide for all available types.
                Defaults to 0 (SIGGEN_RISING)
            triggerSource (int): The source that triggers the signal generator.
                Refer to programmers' guide for all available types.
                Defaults to 1 (SIGGEN_SCOPE_TRIG)
        """

        with open("picoscope/settings.json") as f:
            settings = json.load(f)
        sigGenBuiltIn = settings["sigGenBuiltIn"]

        # Use nondefault params
        for parameter, value in nondefault_params.items():
            sigGenBuiltIn[parameter] = value

        status = ps.ps4000SetSigGenBuiltIn(
            chandle,
            ctypes.c_int32(sigGenBuiltIn['offsetVoltage']),
            ctypes.c_uint32(sigGenBuiltIn['pkToPk']),
            ctypes.c_int16(sigGenBuiltIn['waveType']),
            ctypes.c_float(sigGenBuiltIn['start_freq']),
            ctypes.c_float(sigGenBuiltIn['end_freq']),
            ctypes.c_float(sigGenBuiltIn['increment']),
            ctypes.c_float(sigGenBuiltIn['dwell']),
            ctypes.c_uint16(sigGenBuiltIn['sweepType']),
            ctypes.c_int16(sigGenBuiltIn['operationType']),
            ctypes.c_uint32(sigGenBuiltIn['shots']),
            ctypes.c_uint32(sigGenBuiltIn['sweeps']),
            ctypes.c_wchar_p("SIGGEN_RISING"),
            ctypes.c_wchar_p("SIGGEN_SCOPE_TRIG"),
            ctypes.c_int16(0)
        )

        assert_pico_ok(status)

    def _set_channel_params(self, voltage_range: dict):
        """Sets various channel parameters.

        Args:
            voltage_range (int): Optional. Specifies measuring voltage range [V].
                Refer to programmers' manual for further info.
                Note that I have modified this parameter slightly from the SDK.
                Defaults to 5 [V]
        """

        if not voltage_range.has_key('voltage'):
            voltage_range['voltage'] = 5.0

        parsed_voltage_range = utils.parse_voltage_range(
            numerical_voltage_range=voltage_range['voltage'])

        status = ps.ps4000SetChannel(chandle, self.channel, True, True,
                                     parsed_voltage_range)

        assert_pico_ok(status)

    def _get_timebase(self, timebase: int = 0):
        # Get timebase information
        # Warning: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.
        # To access these Timebases, set any unused analogue channels to off.
        # handle = chandle
        # timebase = 8 = timebase
        # noSamples = maxSamples
        # pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
        # pointer to maxSamples = ctypes.byref(returnedMaxSamples)
        # segment index = 0

        timeIntervalns = ctypes.c_float()
        returnedMaxSamples = ctypes.c_int32()

        status = self.ps.ps4000GetTimebase2(chandle, timebase, self.maxSamples,
                                            ctypes.byref(timeIntervalns),
                                            ctypes.c_int16(1),
                                            ctypes.byref(returnedMaxSamples),
                                            0)

        assert_pico_ok(status)

    def _set_simple_trigger(self,
                            threshold: float = -0.01,
                            direction: str = 'Falling',
                            delay: float = 0.0):
        """Arms the trigger.
        
        Args:

                
        """

        autoTrigger_ms = 100

        status = ps.ps4000SetSimpleTrigger(chandle, 1, self.channel, threshold,
                                           delay, autoTrigger_ms)

        assert_pico_ok(status)

    def _run_block(self,
                   timebase: int = 8,
                   preTriggerSamples: int = 2500,
                   postTriggerSamples: int = 2500):

        # Run block capture
        # handle = chandle
        # number of pre-trigger samples = preTriggerSamples
        # number of post-trigger samples = PostTriggerSamples
        # timebase = 8 = 80 ns = timebase (see Programmer's guide for mre information on timebases)
        # time indisposed ms = None (not needed in the example)
        # segment index = 0
        # lpReady = None (using ps4000IsReady rather than ps4000BlockReady)
        # pParameter = None

        status = ps.ps4000RunBlock(chandle, preTriggerSamples,
                                   postTriggerSamples, timebase,
                                   ctypes.c_int16(1), None, 0, None, None)

        assert_pico_ok(status)

    def _wait_ready(self):
        """Waits for data collection to finish"""

        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        while ready.value == check.value:
            self.status["isReady"] = self.ps.ps4000IsReady(
                chandle, ctypes.byref(ready))

    def _set_data_buffer(self):

        # def set_buffer_location(self):
        #     # Set data buffer location for data collection from channel A
        #     # handle = chandle
        #     # source = PS4000_CHANNEL_A = 0
        #     # pointer to buffer max = ctypes.byref(bufferAMax)
        #     # pointer to buffer min = ctypes.byref(bufferAMin)
        #     # buffer length = maxSamples

        #     bufferMax = (ctypes.c_int16 * self.maxSamples)()
        #     bufferMin = (ctypes.c_int16 * self.maxSamples)() # used for downsampling which isn't in the scope of this example

        buffer_max = (ctypes.c_int16 * self.maxSamples)()
        buffer_min = (ctypes.c_int16 * self.maxSamples
                      )()  # used for downsampling, usually outside this scope

        status = ps.ps4000SetDataBuffers(chandle, 0, ctypes.byref(buffer_max),
                                         ctypes.byref(buffer_min),
                                         self.maxSamples)

        assert_pico_ok(status)

    def _get_data(self, overflow=ctypes.c_int16()):
        # Retrived data from scope to buffers assigned above
        # handle = chandle
        # start index = 0
        # pointer to number of samples = ctypes.byref(cmaxSamples)
        # downsample ratio = 0
        # downsample ratio mode = PS4000_RATIO_MODE_NONE
        # pointer to overflow = ctypes.byref(overflow))

        # create converted type maxSamples
        cmaxSamples = ctypes.c_int32(self.maxSamples)

        status = ps.ps4000GetValues(chandle, 0, ctypes.byref(cmaxSamples), 0,
                                    0, 0, ctypes.byref(overflow))

        assert_pico_ok(status)

    def _stop(self):
        """Stop the scope"""

        status = ps.ps4000Stop(chandle)

        assert_pico_ok(status)

    # def _close(self):
    #     status = ps.ps4000CloseUnit(chandle)

    #     assert_pico_ok(status)

    def sweep(self, params: dict):
        '''Wrapper for frequency sweep.

        Follows recommended block mode procedure as laid out by programmers' guide.

        params (dict): All sweep parameters. See settings for further info

        '''

        # ps.set_averaging(0)

        # ps.set_sample_rate(10*params['end_freq'])
        # sample_rate = utils.set_sample_rate(
        #     xx,
        #     end_freq=params['end_freq']
        # )

        self._set_input_channel(params=params)

        # 1. Open the oscilloscope
        # self.connect()

        # 1.5 Setup
        self._setup(params=params)

        # 2. Select channel ranges and AC/DC coupling
        self._set_channel_params(voltage_range=params)

        # 3. Select timebases
        self._get_timebase()

        # 4. Trigger setup
        self._set_simple_trigger()

        # 5. Start collecting data
        self._run_block()

        # 6. Wait until oscilloscope is ready
        self._wait_ready()

        # 7. Tell the driver where the memory buffer is
        self._set_data_buffer()

        # 8. Transfer data from oscilloscope to PC
        data_adc = self._get_data(self.nsamples)

        maxADC = ctypes.c_int16(32767)

        return adc2mV(bufferMax, chRange, maxADC)

        # 9. Stop oscilloscope
        self._stop()

        # 10. Close unit and disconnect scope
        # self._close()

        return data.tolist()