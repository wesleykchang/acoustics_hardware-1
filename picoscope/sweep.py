"""Implements frequency sweep by calling picoscope functions
in appropriate sequence.
"""

from picoscope.picoscope import Picoscope4000
from picoscope.utils import (get_no_frequencies, parse_voltage_range,
                             set_input_channel, set_sampling_params,
                             ParsedParams)


def sweep(picoscope_: Picoscope4000, params: ParsedParams) -> list:
    '''Wrapper for frequency sweep.

    Follows recommended block mode procedure as
    laid out by programmer's guide.

    Args:
        params (dict): All sweep parameters.
            See settings for further info.

    Example:
        picoscope_ = Picoscope4000()
        picoscope_.connect()
        for _ in range(10):
            data = picoscope_.sweep(params=params)
            *do something w data*
    '''

    channel = set_input_channel(params=params)
    enum_voltage_range = parse_voltage_range(
        numerical_voltage_range=params['voltage_range'])
    no_frequencies = get_no_frequencies(start_freq=params['start_freq'],
                                        end_freq=params['end_freq'],
                                        increment=params['increment'])
    enum_sampling_interval, no_samples = set_sampling_params(
        no_samples=params['max_samples'],
        dwell=params['dwell'],
        no_frequencies=no_frequencies)

    c_buffer = picoscope_.make_buffer(no_samples_=no_samples)

    # 1. Open the oscilloscope
    # This step is implemented in app.py bc we only want to
    # run it upon starting the system, but we sweep a bunch!

    # 1.5 Define signal
    picoscope_.define_procedure(**params)

    # 2. Select channel ranges and AC/DC coupling
    picoscope_.set_channel_params(enum_voltage_range=enum_voltage_range,
                                  channel=channel)

    # 3. Select timebases
    picoscope_.get_timebase(enum_sampling_interval=enum_sampling_interval,
                            no_samples=no_samples)

    # 4. Trigger setup
    picoscope_.set_simple_trigger(channel=channel)

    # 7. Tell the driver where the memory buffer is
    picoscope_.set_data_buffer(channel=channel,
                               no_samples=no_samples,
                               c_buffer=c_buffer)

    # 5. Start collecting data
    picoscope_.run_block(enum_sampling_interval=enum_sampling_interval,
                         no_samples=no_samples)

    # 5.5 Start arbitrary wave generator
    picoscope_.pull_trigger()

    # 6. Wait until oscilloscope is ready
    picoscope_.wait_ready()

    # 8. Transfer data from oscilloscope to PC
    picoscope_.get_data(no_samples=no_samples)

    # 9. Teardown
    picoscope_.stop()

    data_mV = picoscope_.to_mV(enum_voltage_range=enum_voltage_range,
                               no_samples=no_samples,
                               c_buffer=c_buffer)

    return data_mV
