"""Contains wrappers to call picoscope.

Functions with leading underscore should generally not
be called externally (except in tests).
"""

import ctypes
import json
import logging
from picosdk.ps4000 import ps4000 as ps
from picosdk.functions import adc2mV, assert_pico_ok

from picoscope import utils

logging.basicConfig(filename='logs/logs.log',
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')

MAX_SAMPLES = 8192
TIMEBASE = 0
OVERSAMPLE = 1
SEGMENT_INDEX = 0  # zero-based, specifies which memory segment to use

c_handle = ctypes.c_int16()
c_buffer = (ctypes.c_int16 * MAX_SAMPLES)()
c_overflow = ctypes.c_int16()
c_max_samples = ctypes.c_int32(MAX_SAMPLES)


def _set_input_channel(params: dict):
    """Sets the physical input channel, either 0 (A) or 1 (B).
    
    Args:
        params (dict): All sweep parameters. See settings.json.

    Returns:
        channel (int): Because the lazy parsing of params in
            app/get_resonance makes channel a float instead of int.
    """

    if not 'channel' in params:
        channel = 1
    else:
        channel = int(params['channel'])

    return channel


def connect():
    """Connects to oscilloscope.
    
    Note:
        There's an persistent bug where this method fails several times before a connection
        can be established. However, adding a try/except block doesn't solve it.
        The retry must be external, i.e. when running pithy/startup.
    """

    status = ps.ps4000OpenUnit(ctypes.byref(c_handle))

    assert_pico_ok(status)


def _define_procedure(**nondefault_params):
    """Sets up the signal generator to produce a signal from the selected waveType.

    If startFrequency != stopFrequency it will sweep.

    Note:
        All params are optional. Defaults defined in settings.json.
    
    Args:
        offsetVoltage (int): The voltage offset [uV].
            Defaults to 0.
        pkToPk (int): Peak-to-peak voltage [uV].
            Defaults to 2.
        waveType (int): The type of waveform to be generated.
            Refer to programmers' guide for all available types. Defaults to 0 (Sine).
        startFrequency (float): Starting frequency.
            Defaults to 1.0E6.
        stopFrequency (float): Stopping (or reversing) frequency (included).
            Defaults to None.
        increment (float): The amount by which the frequency rises (or falls).
            Defaults to 10.0.
        dwellTime (float): The time [s] between frequency changes.
            Defaults to 1E-3.
        sweepType (int): Determines sweeping type.
            Refer to programmers' guide for all available types. Defaults to 0 (UP).
        operationType (int): Configures white noise generator.
            Refer to programmers' guide for all available types.
            Defaults to 0 (white noise disabled).
        shots (int): The number of cycles of the waveform to be produced after a trigger event.
            If this is set to a non-zero value, then sweeps must be 0. Defaults to 0.
        sweeps (int): Number of sweep repetitions.
            Defaults to None.
        triggerType (int): The type of trigger to be applied to signal generator.
            Refer to programmers' guide for all available types.
            Defaults to 0 (SIGGEN_RISING).
        triggerSource (int): The source that triggers the signal generator.
            Refer to programmers' guide for all available types.
            Defaults to 1 (SIGGEN_SCOPE_TRIG).

    NOTE:
        If a trigger source other than 0 (SIGGEN_NONE) is specified, then either shots or
    sweeps, but not both, must be set to a non-zero value.

    Example:
        picoscope._setup(**params) <- Note the double-star.
    """

    with open("picoscope/settings.json") as f:
        settings = json.load(f)
    signal_params = settings["sigGenBuiltIn"]

    # Use nondefault params
    for parameter, value in nondefault_params.items():
        signal_params[parameter] = value

    if signal_params['end_freq'] > 2E4:
        raise ValueError(f'end_freq cannot be larger than 2E4')

    ext_in_threshold = 0  # Not using so setting to 0

    status = ps.ps4000SetSigGenBuiltIn(
        c_handle, signal_params['offsetVoltage'],
        signal_params['pkToPk'], signal_params['waveType'],
        signal_params['start_freq'], signal_params['end_freq'],
        signal_params['increment'], signal_params['dwell'],
        signal_params['sweepType'], signal_params['operationType'],
        signal_params['shots'], signal_params['sweeps'],
        signal_params['triggerType'], signal_params['triggerSource'],
        ext_in_threshold)

    assert_pico_ok(status)


def _set_channel_params(enum_voltage_range: int, channel: int):
    """Sets various channel parameters.

    Args:
        voltage_range (float): Enum specifying measuring voltage range.
            Refer to programmers' manual for further info.
        channel (int): Oscilloscope channel.
    """

    is_channel = True
    is_dc = True

    status = ps.ps4000SetChannel(c_handle, channel, is_channel, is_dc,
                                 enum_voltage_range)

    assert_pico_ok(status)


def _get_timebase():
    """_summary_

    _extended_summary_

    """

    time_interval_ns = ctypes.c_int32(
        0)  # Not sure on this (see NULL pointes in arg 4)
    returnedMaxSamples = ctypes.c_int32()
    n_samples = MAX_SAMPLES

    status = ps.ps4000GetTimebase2(c_handle, TIMEBASE, n_samples,
                                   ctypes.byref(time_interval_ns),
                                   OVERSAMPLE,
                                   ctypes.byref(returnedMaxSamples),
                                   SEGMENT_INDEX)

    assert_pico_ok(status)


def _set_simple_trigger(threshold: int = 10,
                        direction: int = 3,
                        delay: int = 0,
                        channel: int = 1,
                        autoTrigger_ms: int = 1000):
    """Cocks the gun.

    Args:
        threshold (int, optional): _description_. Defaults to 10.
        direction (int, optional): _description_. Defaults to 3.
        delay (int, optional): _description_. Defaults to 0.
        channel (int, optional): _description_. Defaults to 1.
        autoTrigger_ms (int, optional): _description_. Defaults to 1000.
    """

    enable_trigger = 1

    status = ps.ps4000SetSimpleTrigger(c_handle, enable_trigger,
                                       channel, threshold, direction,
                                       delay, autoTrigger_ms)

    assert_pico_ok(status)


def _run_block():
    """Pulls the trigger: Starts the sweep."""

    pre_trigger_samples = 0
    post_trigger_samples = MAX_SAMPLES
    time_indisposed_ms = 0
    lp_ready = 0
    p_parameter = 0

    status = ps.ps4000RunBlock(c_handle, pre_trigger_samples,
                               post_trigger_samples, TIMEBASE,
                               OVERSAMPLE, time_indisposed_ms,
                               SEGMENT_INDEX, lp_ready, p_parameter)

    assert_pico_ok(status)


def _wait_ready():
    """Waits for data collection to finish before moving onto collecting data."""

    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status = ps.ps4000IsReady(c_handle, ctypes.byref(ready))


def _set_data_buffer(channel):
    """C-type stuff. Allocates memory to receive the oscilloscope to dump from memory.

    Args:
        channel (int): Picoscope channel, either 0 (A) or 1 (B).
    """

    buffer_length = MAX_SAMPLES

    # Note that we use the pseudo-pointer byref
    status = ps.ps4000SetDataBuffer(c_handle, channel,
                                    ctypes.byref(c_buffer),
                                    buffer_length)

    assert_pico_ok(status)


def _get_data():
    """Pulls the data from the oscilloscope."""

    start_index = 0
    downsample_ratio = 0
    downsample_ratio_mode = 0  # None

    status = ps.ps4000GetValues(c_handle, start_index,
                                ctypes.byref(c_max_samples),
                                downsample_ratio,
                                downsample_ratio_mode, SEGMENT_INDEX,
                                ctypes.byref(c_overflow))

    assert_pico_ok(status)


def stop():
    """Stops the picoscope. A necessary step at the end of each sweep."""

    status = ps.ps4000Stop(c_handle)

    assert_pico_ok(status)


def close():
    """Closes the oscilloscope connection, the opposite of connect().

    This method is generally only used for tests.
    """

    status = ps.ps4000CloseUnit(c_handle)

    assert_pico_ok(status)


def to_mV(enum_voltage_range: int, max_ADC: int = 32767):
    """Converts amplitude in ADCs to mV.

    Args:
        enum_voltage_range (int): Enumerated voltage range.
        max_ADC (int, optional): All values are normalized between
            plus/minus max_ADC. No reason to tamper with this!
            Defaults to 32767.

    Returns:
        list: Amplitudes in mV.
    """

    c_max_ADC = ctypes.c_int16(max_ADC)

    return adc2mV(c_buffer, enum_voltage_range, c_max_ADC)


def sweep(params: dict):
    '''Wrapper for frequency sweep.

    Follows recommended block mode procedure as laid out by programmers' guide.

    params (dict): All sweep parameters. See settings for further info.

    Args:
        params (dict): All experiment parameters
    '''

    channel = _set_input_channel(params=params)

    # 1. Open the oscilloscope
    # Calling externally
    # connect()

    # 1.5 Define signal
    _define_procedure(**params)

    enum_voltage_range = utils.parse_voltage_range(
        numerical_voltage_range=params['voltage_range'])

    # 2. Select channel ranges and AC/DC coupling
    _set_channel_params(enum_voltage_range=enum_voltage_range,
                        channel=channel)

    # 3. Select timebases
    _get_timebase()

    # 4. Trigger setup
    _set_simple_trigger()

    # 5. Start collecting data
    _run_block()

    # 6. Wait until oscilloscope is ready
    _wait_ready()

    # 7. Tell the driver where the memory buffer is
    _set_data_buffer(channel=channel)

    # 8. Transfer data from oscilloscope to PC
    _get_data()

    # 9. Stop oscilloscope
    stop()

    data_mV = to_mV(enum_voltage_range=enum_voltage_range)

    return data_mV