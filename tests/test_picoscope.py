import pytest

from picoscope import picoscope

params = {
    'exp_name': 'Kokam-000-2022-04-06',
    'start_freq': 1000.0,
    'end_freq': 19000.0,
    'increment': 100.0,
    'dwell': .001,
    'voltage': 0.2,
    'sweep_interval': 150,
    'c_rate': 1 / 2.,
    'no_cycles': 1,
    'warm_up': 60,
    'rest': 60,
    'channel': 0,
    'voltage_range': 1.0
}


# REMINDER: Pytest runs in sequence which is why we can set up the
# unit tests in this fashion
def test_set_default_input_channel():
    params['channel'] = picoscope._set_input_channel(params=params)

    assert params['channel'] == 0


def test_incorrectly_formatted_input_channel():
    params['channel'] = 'A'
    with pytest.raises(ValueError):
        picoscope._set_input_channel(params=params)


def test_custom_input_channel():
    del params['channel']

    params['channel'] = picoscope._set_input_channel(params=params)

    assert params['channel'] == 1


def test_connect():
    picoscope.connect()


def test_set_channel_params():
    picoscope._set_channel_params(enum_voltage_range=6, channel=1)


def test_get_timebase():
    picoscope._get_timebase()


def test_set_simple_trigger():
    picoscope._set_simple_trigger()


def test_define_procedure():
    picoscope._define_procedure(**params)


def test_run_block():
    picoscope._run_block()


def test_wait_ready():
    picoscope._wait_ready()


def test_set_data_buffer():
    picoscope._set_data_buffer(channel=1)


def test_get_data():
    picoscope._get_data()


def test_to_mV():
    data_in_mV = picoscope.to_mV(enum_voltage_range=1)
    
    assert isinstance(data_in_mV, list)


def test_stop():
    picoscope.stop()


# Integration
def test_sweep():
    resonance_data = picoscope.sweep(params=params)

    assert isinstance(resonance_data, list)


def test_close():
    picoscope.close()
