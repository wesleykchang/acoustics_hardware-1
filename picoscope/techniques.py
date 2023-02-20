"""Implementations of techniques"""

import numpy as np
from typing import Dict

from picoscope.constants import get_builtin_voltage_ranges, get_available_sampling_intervals
from picoscope.constants import PulsingParams, TriggerProperties
from picoscope.picoscope import Picoscope2000
from picoscope.utils import parse_to_enum

SAMPLING_INTERVAL: float = 2E-9


def _run(picoscope_: Picoscope2000, enum_voltage_range: int, enum_sampling_interval: int, trigger_properties: TriggerProperties, avg_num: int) -> np.ndarray:
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
        list[float]: Results from pulse
    """
    # should we here have an anlogue shift? I don't think it's necessary, but need to test

    picoscope_.set_averaging(avg_num=avg_num)
    picoscope_.setup_signal()
    picoscope_.set_channel(enum_voltage_range=enum_voltage_range)
    picoscope_.set_simple_trigger(trigger_properties=trigger_properties)

    waveforms_mV = np.zeros((avg_num, picoscope_.n_samples))

    for segment in range(avg_num):
        picoscope_.set_segment_index(segment=segment)
        picoscope_.check_timebase()  # segment index
        c_buffer = picoscope_.make_buffer()
        picoscope_.set_data_buffer(c_buffer=c_buffer)  # segment index
        picoscope_.run_block(enum_sampling_interval=enum_sampling_interval)  # segment index
        picoscope_.pull_trigger()
        picoscope_.wait_ready()
        picoscope_.get_data()  # segment index
        picoscope_.stop()
        waveform = picoscope_.to_mV(
            enum_voltage_range=enum_voltage_range,
            c_buffer=c_buffer
        )
        waveforms_mV[segment, :] = waveform

    return waveforms_mV


def pulse(picoscope_: Picoscope2000, pulsing_params: PulsingParams) -> Dict[str, float]:
    """Wrapper for acoustic pulsing.

    Follows recommended block mode procedure as
    laid out by programmer's guide.

    Args:
        picoscope_ (Picoscope2000): Picoscope instance.

    Returns:
        list[float]: Results from pulse.
    """

    picoscope_.set_n_samples(duration=pulsing_params.duration)
    enum_voltage_range = parse_to_enum(
        arr_fn=get_builtin_voltage_ranges,
        val=pulsing_params.voltage
    )
    enum_sampling_interval = parse_to_enum(
        arr_fn=get_available_sampling_intervals,
        val=SAMPLING_INTERVAL
    )
    trigger_properties = TriggerProperties()
    trigger_properties.set_delay(
        delay_us=pulsing_params.delay,
        sampling_interval=SAMPLING_INTERVAL
    )

    waveforms_mV = _run(
        picoscope_=picoscope_,
        enum_voltage_range=enum_voltage_range,
        enum_sampling_interval=enum_sampling_interval,
        trigger_properties=trigger_properties,
        avg_num=pulsing_params.avg_num
    )

    payload = dict()
    payload['amps'] = np.mean(waveforms_mV, axis=0).tolist()

    return payload
