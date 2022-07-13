import pytest

from picoscope import picoscope

params = {
    'exp_name': 'Kokam-000-2022-04-06',
    'start_freq': 1000,
    'end_freq': 21000,
    'increment': 100,
    'dwell': .001,
    'voltage': 0.2,
    'sweep_interval': 150,
    'c_rate': 1 / 2.,
    'no_cycles': 1,
    'warm_up': 60,
    'rest': 60,
    'channel': 'A'
}

@pytest.fixture
def instance():
    picoscope_ = picoscope.Picoscope()

    return picoscope_

def test_class_instance(instance):
    assert isinstance(instance, picoscope.Picoscope)

# REMINDER: Pytest runs in sequence which is why we can set up the
# unit tests in this fashion
def test_set_default_input_channel(instance):
    instance._set_input_channel(params)

    assert instance.channel == 'A'

def test_set_custom_input_channel(instance):
    del params['channel']

    instance._set_input_channel(params)
    instance._set_input_channel

    assert instance.channel == 'B'

def test_connect(instance):
    instance.connect()

def test_stop(instance):
    instance._stop()

def test_setup(instance):
    instance._setup()

# def test_set_channel_params(instance):
#     instance._set_channel_params()

# def test_get_timebase(instance):
#     instance._get_timebase()

# def test_set_simple_trigger(instance):
#     instance._set_simple_trigger()

# def test_run_block(instance):
#     instance._run_block()

# def test_wait_ready(instance):
#     instance._wait_ready()

# def test_set_data_buffer(instance):
#     instance._set_data_buffer()

# def test_get_data():
#     instance._get_data()

# # Integration
# def test_sweep(instance):
#     instance.sweep(params=params)
