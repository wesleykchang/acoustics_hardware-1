"""Contains functions for calling picoscope."""

import ctypes
import json
from picosdk.errors import PicoSDKCtypesError
from picosdk.PicoDeviceEnums import picoEnum as enums
from picosdk.functions import adc2mV, assert_pico_ok
from picosdk.ps4000 import ps4000 as ps

from picoscope import utils

C_OVERSAMPLE = ctypes.c_int16(1)
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
        Looping because the connection process
        mistifyingly always fails on the first try.
    """

    for _ in range(3):
        try:
            status = ps.ps4000OpenUnit(ctypes.byref(c_handle))
            assert_pico_ok(status)
            break
        except PicoSDKCtypesError:
            continue


def define_procedure(ext_in_threshold: int = 0,
                     operation_type: int = 0,
                     **nondefault_params):
    """Sets up the signal generator to produce a waveType signal.

    If startFrequency != stopFrequency it will sweep.

    Note:
        All params are optional. Defaults defined in settings.json.
    
    Args:
        ext_in_threshold (int): Generally not used so kept as 0.
        operation_type (int): Generally not used to kept as 0
            (disable white-noise). 
        offset_voltage (int): The voltage offset [uV].
            Defaults to 0.
        pk_to_pk (int): Peak-to-peak voltage [uV].
            Defaults to 2E6.
        wave_type (int): The type of waveform to be generated.
            Refer to programmer's guide for all available types.
            Defaults to 0 (Sine).
        start_freq (float): Starting frequency.
            Defaults to 1.0E6.
        end_freq (float): Stopping (or reversing) frequency (included).
            Defaults to None.
        increment (float): The amount by which the frequency rises (or falls).
            Defaults to 10.0.
        dwell_time (float): The time [s] between frequency changes.
            Defaults to 1E-3.
        dwell_time (str): Determines sweeping type.
            Refer to programmer's guide for all available types.
            Defaults to PICO_UP.
        shots (int): The number of cycles of the waveform to be produced
            after a trigger event. Defaults to 1.
        sweeps (int): Number of sweep repetitions.
            Defaults to 0.
        trigger_type (int): The type of trigger to be applied to signal
            generator. Refer to programmer's guide for all available types.
            Defaults to 1 (SIGGEN_FALLING).
        trigger_source (str): The source that triggers the signal generator.
            Refer to programmer's guide for all available types.
            Defaults to SIGGEN_SCOPE_TRIG.

    NOTE:
        If a trigger source other than 0 (SIGGEN_NONE) is specified,
        then either shots or sweeps, but not both, must be set to a
        non-zero value.

    Raises:
        ValueError: If end_freq>2E4 [Hz].

    Example:
        picoscope.define_procedure(**params) <- Note the kwargs (double-star).
    """

    with open("picoscope/settings.json") as f:
        settings = json.load(f)
    sig_params = settings["sigGenBuiltIn"]

    # Use nondefault params
    for parameter, value in nondefault_params.items():
        sig_params[parameter] = value

    if sig_params['end_freq'] > 2E4:
        raise ValueError(f'end_freq cannot be larger than 2E4')

    # Enum to change str to ints
    sweep_type = enums.PICO_SWEEP_TYPE[sig_params['sweep_type']]
    trigger_source = enums.PICO_SIGGEN_TRIG_SOURCE[
        sig_params['trigger_source']]
    # Ugh, the library doesn't have this for wavetype and triggertype?
    wave_type = utils.WaveType[sig_params['wave_type']].value
    trigger_type = utils.TriggerType[sig_params['trigger_type']].value

    status = ps.ps4000SetSigGenBuiltIn(
        c_handle, sig_params['offset_voltage'],
        int(sig_params['pk_to_pk']), wave_type,
        sig_params['start_freq'], sig_params['end_freq'],
        sig_params['increment'], sig_params['dwell'], sweep_type,
        operation_type, sig_params['shots'], sig_params['sweeps'],
        trigger_type, trigger_source, ext_in_threshold)

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


def get_timebase(enum_sampling_interval: int):
    """Basically sets the sampling rate.

    There's a whole section devoted to this subject in the
    programmer's guide.

    Args:
        enum_sampling_rate (int): Enumerated sampling rate.
            See utils.calculate_sampling_rate().
    """

    time_interval_ns = ctypes.c_int32()
    c_max_samples = ctypes.c_int32(max_samples)
    n_samples = max_samples

    status = ps.ps4000GetTimebase(c_handle, enum_sampling_interval,
                                  n_samples,
                                  ctypes.byref(time_interval_ns),
                                  C_OVERSAMPLE,
                                  ctypes.byref(c_max_samples),
                                  SEGMENT_INDEX)

    print(time_interval_ns)
    assert_pico_ok(status)


def set_simple_trigger(channel: int,
                       threshold: int = 300,
                       direction: int = "PICO_RISING_OR_FALLING",
                       delay: int = 0,
                       autoTrigger_ms: int = 1000,
                       enable_trigger: int = 1):
    """Cocks the gun.

    Args:
        channel (int): Picoscope channel, either 0 (A) or 1 (B).
        threshold (int, optional): The ADC count at which the
            trigger will fire. Defaults to 300.
        direction (str, optional): The direction in which the
            signal must move to cause a trigger.
            Defaults to PICO_RISING_OR_FALLING.
        delay (int, optional): The time, in sample periods,
            between the trigger occuring and the first sample
            being taken. Defaults to 0.
        autoTrigger_ms (int, optional): The number of milliseconds
            the device will wait if no trigger occurs.
            Defaults to 1000.
        enable_trigger (int, optional): Whether to enable trigger
            or not. Not used so don't mess with. Defaults to 1.
    """

    threshold_direction = enums.PICO_THRESHOLD_DIRECTION[direction]

    status = ps.ps4000SetSimpleTrigger(c_handle, enable_trigger,
                                       channel, threshold,
                                       threshold_direction, delay,
                                       autoTrigger_ms)

    assert_pico_ok(status)


def run_block(enum_sampling_interval: int):
    """Starts collecting data.
    
    enum_sampling_rate (int): Enumerated sampling rate.
        See utils.calculate_sampling_rate().
    """

    pre_trigger_samples = 0
    post_trigger_samples = max_samples
    time_indisposed_ms = None
    lp_ready = None
    p_parameter = None

    status = ps.ps4000RunBlock(c_handle, pre_trigger_samples,
                               post_trigger_samples,
                               enum_sampling_interval, C_OVERSAMPLE,
                               time_indisposed_ms, SEGMENT_INDEX,
                               lp_ready, p_parameter)

    assert_pico_ok(status)


def pull_trigger():
    """Pulls the trigger: Starts the sweep.
    
    Triggers the wave generator.
    """

    state = 1

    status = ps.ps4000SigGenSoftwareControl(c_handle, state)

    assert_pico_ok(status)


def block_ready(c_handle, status_, p_parameter):

    ps.ps4000BlockReady(c_handle, status_, p_parameter)


def wait_ready():
    """Waits for data collection to finish before data is collected."""

    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status = ps.ps4000IsReady(c_handle, ctypes.byref(ready))

        assert_pico_ok(status)


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


def stop():
    """Stops the picoscope, a necessary step at the end of each sweep.
    """

    status = ps.ps4000Stop(c_handle)

    assert_pico_ok(status)


def disconnect():
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
