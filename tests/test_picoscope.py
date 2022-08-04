import json
import pytest

from picoscope import picoscope, utils

with open("tests/params.json") as f:
    params = json.load(f)

CHANNEL = 1
enum_sampling_interval = 9
enum_voltage_range = 6


def test_globals():
    picoscope.set_globals(samples_max=params['max_samples'])


def test_connect():
    picoscope.connect()  # Assertion called implicitly in function


def test_set_channel_params():
    picoscope.set_channel_params(
        enum_voltage_range=enum_voltage_range, channel=CHANNEL)


@pytest.fixture
def no_frequencies():
    no_frequencies = utils.get_no_frequencies(
        start_freq=params['start_freq'],
        end_freq=params['end_freq'],
        increment=params['increment'])

    return no_frequencies


@pytest.fixture
def enum_sampling_interval(no_frequencies):
    enum_sampling_interval = utils.calculate_sampling_interval(
        max_samples=params['max_samples'],
        dwell=params['dwell'],
        no_frequencies=no_frequencies)

    return enum_sampling_interval


def test_get_timebase(enum_sampling_interval):
    picoscope.get_timebase(
        enum_sampling_interval=enum_sampling_interval)


def test_set_simple_trigger():
    picoscope.set_simple_trigger(channel=CHANNEL)


def test_define_procedure():
    picoscope.define_procedure(**params)


def test_set_data_buffer():
    picoscope.set_data_buffer(channel=CHANNEL)


def test_run_block(enum_sampling_interval):
    picoscope.run_block(enum_sampling_interval=enum_sampling_interval)


def test_trigger_pull():
    picoscope.pull_trigger()


def test_wait_ready():
    picoscope.wait_ready()


def test_get_data():
    picoscope.get_data()


def test_stop():
    picoscope.stop()


def test_to_mV():
    data_in_mV = picoscope.to_mV(enum_voltage_range=1)

    assert isinstance(data_in_mV, list)


def test_close():
    picoscope.disconnect()
