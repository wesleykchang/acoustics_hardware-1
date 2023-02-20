"""Implementations of techniques"""

from picoscope.constants import get_builtin_voltage_ranges, get_available_sampling_intervals
from picoscope.constants import PulsingParams, SignalProperties, TriggerProperties
from picoscope.picoscope import Picoscope2000
from picoscope.utils import parse_to_enum

SAMPLING_INTERVAL: int = int(2E-9)


def _run(picoscope_: Picoscope2000, enum_voltage_range: int, enum_sampling_interval: int, trigger_properties: TriggerProperties) -> list:
    """Low-level implementation of oscilloscope techniques.

    Follows procedure as laid out in Picoscope SDK manual, aside from
    opening the oscilloscope separately b/c there's a little bit of a time
    tax to it and we only need to run that particular function once, whereas
    we pulse a bunch of times.

    Args:
        picoscope_ (Union[Picoscope2000, Picoscope4000]): Picoscope instance,
            either 2000-level or 4000-level.
        enum_voltage_range (int): Enumerated voltage.
        channel (int): Channel number.
        enum_sampling_interval (int): Enumerated sampling interval.
        no_samples (int): Number of samples to collect.

    Returns:
        list[float]: Results from pulse/sweep/what-you-wanna-call-it.
    """
    # should we here have an anlogue shift? I don't think it's necessary, but need to test

    picoscope_.define_procedure()
    picoscope_.set_channel(enum_voltage_range=enum_voltage_range)
    picoscope_.check_timebase()
    picoscope_.set_simple_trigger(trigger_properties=trigger_properties)
    c_buffer = picoscope_.make_buffer()
    picoscope_.set_data_buffer(c_buffer=c_buffer)
    picoscope_.run_block(enum_sampling_interval=enum_sampling_interval)
    picoscope_.pull_trigger()
    picoscope_.wait_ready()
    picoscope_.get_data()
    picoscope_.stop()
    data_mV = picoscope_.to_mV(
        enum_voltage_range=enum_voltage_range,
        c_buffer=c_buffer
    )

    return data_mV


def pulse(picoscope_: Picoscope2000, pulsing_params: PulsingParams) -> list:
    """Wrapper for acoustic pulsing.

    Follows recommended block mode procedure as
    laid out by programmer's guide.

    Args:
        picoscope_ (Picoscope2000): Picoscope instance.

    Returns:
        list[float]: Results from pulse.
    """

    picoscope_.set_n_samples(duration=pulsing_params.duration)
    trigger_properties = TriggerProperties(
        delay=PulsingParams.delay
    )
    enum_voltage_range = parse_to_enum(
        arr=get_builtin_voltage_ranges(),
        val=pulsing_params.voltage
    )
    enum_sampling_interval = parse_to_enum(
        arr=get_available_sampling_intervals(),
        val=SAMPLING_INTERVAL
    )
    # delay = 
    # avg_num = 
    # duration = 
    # Set delay, avg_num & duration

    data_mV = _run(
        picoscope_=picoscope_,
        enum_voltage_range=enum_voltage_range,
        enum_sampling_interval=enum_sampling_interval,
        trigger_properties=trigger_properties
    )

    return data_mV

