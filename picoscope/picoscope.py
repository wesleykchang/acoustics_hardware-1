"""Contains functions for calling picoscope."""

import ctypes
import json
from picosdk.errors import PicoSDKCtypesError
from picosdk.functions import adc2mV, assert_pico_ok
from picosdk.ps4000 import ps4000 as ps

TIMEBASE = 0
OVERSAMPLE = 1
SEGMENT_INDEX = 0  # specifies which memory segment to use

c_handle = ctypes.c_int16()
c_overflow = ctypes.c_int16()


def set_globals(samples_max: int):
    """Sets global variables

    I hate using globals, but I can't figure out a different
    way of varying max_samples because of c_buffer
    and c_max_samples.

    Args:
        samples_max (int): Maximum number of samples to be collected.
    """

    global max_samples, c_buffer, c_max_samples

    max_samples = int(samples_max)
    c_buffer = (ctypes.c_int16 * max_samples)()
    c_max_samples = ctypes.c_int32(max_samples)


def connect():
    """Connects to oscilloscope.

    NOTE:
        The loop is in place because mistifyingly the connection
        process almost always fails on the first try.
    """

    for _ in range(3):
        try:
            status = ps.ps4000OpenUnit(ctypes.byref(c_handle))
            assert_pico_ok(status)
            break
        except PicoSDKCtypesError:
            continue


def define_procedure(**nondefault_params):
    """Sets up the signal generator to produce a waveType signal.

    If startFrequency != stopFrequency it will sweep.

    Note:
        All params are optional. Defaults defined in settings.json.
    
    Args:
        offsetVoltage (int): The voltage offset [uV].
            Defaults to 0.
        pkToPk (int): Peak-to-peak voltage [uV].
            Defaults to 2.
        waveType (int): The type of waveform to be generated.
            Refer to programmer's guide for all available types.
            Defaults to 0 (Sine).
        startFrequency (float): Starting frequency.
            Defaults to 1.0E6.
        stopFrequency (float): Stopping (or reversing) frequency (included).
            Defaults to None.
        increment (float): The amount by which the frequency rises (or falls).
            Defaults to 10.0.
        dwellTime (float): The time [s] between frequency changes.
            Defaults to 1E-3.
        sweepType (int): Determines sweeping type.
            Refer to programmer's guide for all available types.
            Defaults to 0 (UP).
        operationType (int): Configures white noise generator.
            Refer to programmer's guide for all available types.
            Defaults to 0 (white noise disabled).
        shots (int): The number of cycles of the waveform to be produced
            after a trigger event. Defaults to 1.
        sweeps (int): Number of sweep repetitions.
            Defaults to 0.
        triggerType (int): The type of trigger to be applied to signal
            generator. Refer to programmer's guide for all available types.
            Defaults to 1 (SIGGEN_FALLING).
        triggerSource (int): The source that triggers the signal generator.
            Refer to programmer's guide for all available types.
            Defaults to 1 (SIGGEN_SCOPE_TRIG).

    NOTE:
        If a trigger source other than 0 (SIGGEN_NONE) is specified,
        then either shots or sweeps, but not both, must be set to a
        non-zero value.

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
        int(signal_params['pkToPk']), signal_params['waveType'],
        signal_params['start_freq'], signal_params['end_freq'],
        signal_params['increment'], signal_params['dwell'],
        signal_params['sweepType'], signal_params['operationType'],
        signal_params['shots'], signal_params['sweeps'],
        signal_params['triggerType'], signal_params['triggerSource'],
        ext_in_threshold)

    assert_pico_ok(status)


def set_channel_params(enum_voltage_range: int, channel: int):
    """Sets various channel parameters.

    Args:
        enum_voltage_range (int): Enum specifying measuring voltage range.
            Refer to programmer's manual for further info.
        channel (int): Picoscope channel, either 0 (A) or 1 (B).
    """

    is_channel = True
    is_dc = True

    status = ps.ps4000SetChannel(c_handle, channel, is_channel, is_dc,
                                 enum_voltage_range)

    assert_pico_ok(status)


def get_timebase():
    """Basically sets the sampling rate.

    There's a whole section devoted to this subject in the
    programmer's guide.
    """

    time_interval_ns = ctypes.c_int32(0)
    returnedMaxSamples = ctypes.c_int32()
    n_samples = max_samples

    status = ps.ps4000GetTimebase2(c_handle, TIMEBASE, n_samples,
                                   ctypes.byref(time_interval_ns),
                                   OVERSAMPLE,
                                   ctypes.byref(returnedMaxSamples),
                                   SEGMENT_INDEX)

    assert_pico_ok(status)


def set_simple_trigger(channel: int,
                       threshold: int = 300,
                       direction: int = 4,
                       delay: int = 0,
                       autoTrigger_ms: int = 1000):
    """Cocks the gun.

    Args:
        channel (int): Picoscope channel, either 0 (A) or 1 (B).
        threshold (int, optional): The ADC count at which the
            trigger will fire. Defaults to 300.
        direction (int, optional): The direction in which the
            signal must move to cause a trigger.
            Defaults to 4 (RISING_OR_FALLING).
        delay (int, optional): The time, in sample periods,
            between the trigger occuring and the first sample
            being taken. Defaults to 0.
        autoTrigger_ms (int, optional): The number of milliseconds
            the device will wait if no trigger occurs.
            Defaults to 1000.
    """

    enable_trigger = 1

    status = ps.ps4000SetSimpleTrigger(c_handle, enable_trigger,
                                       channel, threshold, direction,
                                       delay, autoTrigger_ms)

    assert_pico_ok(status)


def run_block():
    """Starts collecting data."""

    pre_trigger_samples = 0
    post_trigger_samples = max_samples
    time_indisposed_ms = 0
    lp_ready = 0
    p_parameter = 0

    status = ps.ps4000RunBlock(c_handle, pre_trigger_samples,
                               post_trigger_samples, TIMEBASE,
                               OVERSAMPLE, time_indisposed_ms,
                               SEGMENT_INDEX, lp_ready, p_parameter)

    assert_pico_ok(status)


def pull_trigger():
    """Pulls the trigger: Starts the sweep.
    
    Triggers the arbitrary wave generator.
    """

    state = 1

    status = ps.ps4000SigGenSoftwareControl(c_handle, state)

    assert_pico_ok(status)


def wait_ready():
    """Waits for data collection to finish before collecting data."""

    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status = ps.ps4000IsReady(c_handle, ctypes.byref(ready))


def set_data_buffer(channel: int):
    """Allocates memory to receive the oscilloscope to dump from memory.

    C-type stuff.

    Args:
        channel (int): Picoscope channel, either 0 (A) or 1 (B).
    """

    buffer_length = max_samples

    # Note that we use the pseudo-pointer byref
    status = ps.ps4000SetDataBuffer(c_handle, channel,
                                    ctypes.byref(c_buffer),
                                    buffer_length)

    assert_pico_ok(status)


def get_data():
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


def teardown():
    offset_voltage = 0
    pk_to_pk = 0
    wave_type = 8  # DC
    start_freq = 0
    end_freq = 0
    increment = 0
    dwell = 0
    sweep_type = 0
    operation_type = 0
    shots = 1
    sweeps = 0
    trigger_type = 1  # FALLING
    trigger_source = 1  # Software
    ext_in_threshold = 0

    status = ps.ps4000SetSigGenBuiltIn(
        c_handle, offset_voltage, pk_to_pk, wave_type, start_freq,
        end_freq, increment, dwell, sweep_type, operation_type, shots,
        sweeps, trigger_type, trigger_source, ext_in_threshold)

    assert_pico_ok(status)


def stop():
    """Stops the picoscope, a necessary step at the end of each sweep.
    """

    status = ps.ps4000Stop(c_handle)

    assert_pico_ok(status)


def close():
    """Closes the oscilloscope connection, the opposite of connect().

    Generally speaking, this should only be used for tests.
    """

    status = ps.ps4000CloseUnit(c_handle)

    assert_pico_ok(status)


def to_mV(enum_voltage_range: int):
    """Converts amplitude in ADCs to mV.

    Args:
        enum_voltage_range (int): Enumerated voltage range.

    Returns:
        list: Amplitudes in mV.
    """

    c_max_ADC = ctypes.c_int16(max_samples)

    return adc2mV(c_buffer, enum_voltage_range, c_max_ADC)
