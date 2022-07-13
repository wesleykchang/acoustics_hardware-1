"""Contains wrappers to call picoscope.

Functions with leading underscore should generally not
be called externally (except in tests).
"""

import ctypes
import json
import logging
from picosdk.ps4000 import ps4000 as ps
from picosdk.functions import adc2mV, assert_pico_ok

import picoscope.utils as utils

logging.basicConfig(filename='logs/logs.log',
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')

chandle = ctypes.c_int16()
MAX_SAMPLES = 8192
buffer = (ctypes.c_int16 * MAX_SAMPLES)()
overflow = ctypes.c_int16()
c_max_samples = ctypes.c_int32(MAX_SAMPLES)


def _set_input_channel(params: dict):
    """Sets the physical input channel (either A or B).
    
    Args:
        params (dict): All sweep parameters. See settings for further info
    """


    if not 'channel' in params:
        channel = 1
    else:
        # int() because the lazy parsing of params I do in app/get_resonance
        # makes 'channel' a float instead of int
        channel = int(params['channel'])

    return channel


def connect():
    """Connects to oscilloscope.
    
    Note:
        There's an persistent bug where this method fails several times before a connection
        can be established. However, adding a try/except block doesn't solve it.
        The retry must be external, i.e. when running pithy/startup
    """

    status = ps.ps4000OpenUnit(ctypes.byref(chandle))

    assert_pico_ok(status)


def _define_procedure(**nondefault_params):
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
        sweepType (int): Determines sweeping type.
            Refer to programmers' guide for all available types. Defaults to 0 (UP)
        operationType (int): Configures white noise generator.
            Refer to programmers' guide for all available types.
            Defaults to 0 (white noise disabled)
        shots (int): The number of cycles of the waveform to be produced after a trigger event.
            If this is set to a non-zero value, then sweeps must be 0. Defaults to 0.
        sweeps (int): Number of sweep repetitions.
            Defaults to None
        triggerType (int): The type of trigger to be applied to signal generator.
            Refer to programmers' guide for all available types.
            Defaults to 0 (SIGGEN_RISING)
        triggerSource (int): The source that triggers the signal generator.
            Refer to programmers' guide for all available types.
            Defaults to 1 (SIGGEN_SCOPE_TRIG)

    NOTE:
        If a trigger source other than 0 (SIGGEN_NONE) is specified, then either shots or
    sweeps, but not both, must be set to a non-zero value.

    Example:
        picoscope._setup(**params) <- Note the double-star
    """

    with open("picoscope/settings.json") as f:
        settings = json.load(f)
    signal_params = settings["sigGenBuiltIn"]

    # Use nondefault params
    for parameter, value in nondefault_params.items():
        signal_params[parameter] = value

    status = ps.ps4000SetSigGenBuiltIn(
        chandle, signal_params['offsetVoltage'], signal_params['pkToPk'],
        signal_params['waveType'], signal_params['start_freq'],
        signal_params['end_freq'], signal_params['increment'],
        signal_params['dwell'], signal_params['sweepType'],
        signal_params['operationType'], signal_params['shots'],
        signal_params['sweeps'], signal_params['triggerType'],
        signal_params['triggerSource'], 0)

    assert_pico_ok(status)


def _set_channel_params(voltage_range: float = 5.0, channel: int = 1):
    """Sets various channel parameters.

    Args:
        voltage_range (int): Optional. Specifies measuring voltage range [V].
            Refer to programmers' manual for further info.
            Note that I have modified this parameter slightly from the SDK.
            Defaults to 5 [V]
        channel (1): Optional. Oscilloscope channel. Defaults to 1 ('B')
    """

    categorized_voltage_range = utils.parse_voltage_range(
        numerical_voltage_range=voltage_range)

    status = ps.ps4000SetChannel(chandle, channel, 1, 1,
                                 categorized_voltage_range)

    assert_pico_ok(status)

    return categorized_voltage_range


def _get_timebase(timebase: int = 0):
    # Get timebase information
    # Warning: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.
    # To access these Timebases, set any unused analogue channels to off.
    # handle = chandle
    # timebase = 8 = timebase
    # noSamples = maxSamples
    # pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
    # pointer to maxSamples = ctypes.byref(returnedMaxSamples)
    # segment index = 0

    # timeIntervalns = ctypes.c_float()  # Not sure on this (see NULL pointes in arg 4)
    returnedMaxSamples = ctypes.c_int32()
    oversample = 1  # Not sure on this

    status = ps.ps4000GetTimebase2(chandle, timebase, MAX_SAMPLES,
                                   ctypes.byref(ctypes.c_int32(0)), oversample,
                                   ctypes.byref(returnedMaxSamples), 0)

    assert_pico_ok(status)


def _set_simple_trigger(threshold: int = 10,
                        direction: int = 3,
                        delay: int = 0,
                        channel: int = 1,
                        autoTrigger_ms: int = 100):
    """Arms the trigger.
    
    Args:

            
    """

    status = ps.ps4000SetSimpleTrigger(chandle, 1, channel, threshold,
                                       direction, delay, autoTrigger_ms)

    assert_pico_ok(status)


def _run_block(timebase: int = 8,
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

    status = ps.ps4000RunBlock(chandle, preTriggerSamples, postTriggerSamples,
                               timebase, 0, 0, 0, 0, 0)

    assert_pico_ok(status)


def _wait_ready():
    """Waits for data collection to finish"""

    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status = ps.ps4000IsReady(chandle, ctypes.byref(ready))


def _set_data_buffer(channel: int = 1):

    # def set_buffer_location(self):
    #     # Set data buffer location for data collection from channel A
    #     # handle = chandle
    #     # source = PS4000_CHANNEL_A = 0
    #     # pointer to buffer max = ctypes.byref(bufferAMax)
    #     # pointer to buffer min = ctypes.byref(bufferAMin)
    #     # buffer length = maxSamples

    #     bufferMax = (ctypes.c_int16 * maxSamples)()
    #     bufferMin = (ctypes.c_int16 * maxSamples)() # used for downsampling which isn't in the scope of this example

    bufferLth = MAX_SAMPLES

    status = ps.ps4000SetDataBuffer(chandle, channel, ctypes.byref(buffer),
                                    bufferLth)

    assert_pico_ok(status)


def _get_data():
    # Retrived data from scope to buffers assigned above
    # handle = chandle
    # start index = 0
    # pointer to number of samples = ctypes.byref(cmaxSamples)
    # downsample ratio = 0
    # downsample ratio mode = PS4000_RATIO_MODE_NONE
    # pointer to overflow = ctypes.byref(overflow))

    status = ps.ps4000GetValues(chandle, 0, ctypes.byref(c_max_samples), 0, 0,
                                0, ctypes.byref(overflow))

    assert_pico_ok(status)


def _stop():
    """Stop the scope"""

    status = ps.ps4000Stop(chandle)

    assert_pico_ok(status)


def close():
    status = ps.ps4000CloseUnit(chandle)

    assert_pico_ok(status)


def to_mV(categorized_voltage_range):
    maxADC = ctypes.c_int16(32767)

    return adc2mV(buffer, categorized_voltage_range, maxADC)


def sweep(params: dict):
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

    _set_input_channel(params=params)

    # 1. Open the oscilloscope
    # Calling externally
    # connect()

    # 1.5 Define signal
    _define_procedure(**params)

    # 2. Select channel ranges and AC/DC coupling
    categorized_voltage_range = _set_channel_params(voltage_range=params['voltage_range'])

    # 3. Select timebases
    _get_timebase()

    # 4. Trigger setup
    _set_simple_trigger()

    # 5. Start collecting data
    _run_block()

    # 6. Wait until oscilloscope is ready
    _wait_ready()

    # 7. Tell the driver where the memory buffer is
    _set_data_buffer()

    # 8. Transfer data from oscilloscope to PC
    _get_data()

    # 9. Stop oscilloscope
    _stop()

    data_mV = to_mV(categorized_voltage_range=categorized_voltage_range)

    return data_mV