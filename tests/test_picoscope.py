import json
import pytest

from picoscope import picoscope, utils

with open("tests/params.json") as f:
    params = json.load(f)

CHANNEL = 1
sampling_params = 9
enum_voltage_range = 6


@pytest.fixture
def sampling_params(no_frequencies):
    enum_sampling_interval, no_samples = utils.set_sampling_params(
        no_samples=params['max_samples'],
        dwell=params['dwell'],
        no_frequencies=no_frequencies)

    return enum_sampling_interval, no_samples


def test_globals(sampling_params):
    picoscope.set_globals(no_samples_=sampling_params[1])


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


def test_get_timebase(sampling_params):
    picoscope.get_timebase(
        enum_sampling_interval=sampling_params[0])


def test_set_simple_trigger():
    picoscope.set_simple_trigger(channel=CHANNEL)


def test_define_procedure():
    picoscope.define_procedure(**params)


def test_set_data_buffer():
    picoscope.set_data_buffer(channel=CHANNEL)


def test_run_block(sampling_params):
    picoscope.run_block(enum_sampling_interval=sampling_params[0])


def test_trigger_pull():
    picoscope.pull_trigger()


def test_wait_ready():
    picoscope.wait_ready()


def test_get_data():
    picoscope.get_data()


def test_stop():
    picoscope.stop()


def test_to_mV():
    data_in_mV = picoscope.to_mV(enum_voltage_range=enum_voltage_range)

    assert isinstance(data_in_mV, list)


def test_close():
    picoscope.disconnect()
