"""Implements frequency sweep by calling picoscope functions
in appropriate sequence
"""

from picoscope import picoscope, utils


def sweep(params: dict):
    '''Binding for frequency sweep.

    Follows recommended block mode procedure as
    laid out by programmer's guide.

    params (dict): All sweep parameters.
        See settings for further info.

    Args:
        params (dict): All experiment parameters

    Example:
        picoscope.connect()
        for _ in range(10):
            picoscope.sweep(params=params)
    '''

    channel = utils.set_input_channel(params=params)

    no_frequencies = utils.get_no_frequencies(
        start_freq=params['start_freq'],
        end_freq=params['end_freq'],
        increment=params['increment'])
    enum_sampling_interval, no_samples = utils.set_sampling_params(
        no_samples=params['max_samples'],
        dwell=params['dwell'],
        no_frequencies=no_frequencies)

    picoscope.set_globals(no_samples_=no_samples)

    # 1. Open the oscilloscope

    # 1.5 Define signal
    picoscope.define_procedure(**params)

    enum_voltage_range = utils.parse_voltage_range(
        numerical_voltage_range=params['voltage_range'])

    # 2. Select channel ranges and AC/DC coupling
    picoscope.set_channel_params(
        enum_voltage_range=enum_voltage_range, channel=channel)

    # 3. Select timebases
    picoscope.get_timebase(
        enum_sampling_interval=enum_sampling_interval)

    # 4. Trigger setup
    picoscope.set_simple_trigger(channel=channel)

    # 7. Tell the driver where the memory buffer is
    picoscope.set_data_buffer(channel=channel)

    # 5. Start collecting data
    picoscope.run_block(enum_sampling_interval=enum_sampling_interval)

    # 5.5 Start arbitrary wave generator
    picoscope.pull_trigger()

    # 6. Wait until oscilloscope is ready
    picoscope.wait_ready()

    # 8. Transfer data from oscilloscope to PC
    picoscope.get_data()

    # 9. Teardown
    picoscope.stop()

    data_mV = picoscope.to_mV(enum_voltage_range=enum_voltage_range)

    return data_mV
