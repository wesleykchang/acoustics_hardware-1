import json
import pytest

from picoscope import utils
from picoscope.picoscope import Picoscope4000

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


@pytest.fixture
def picoscope_():
    picoscope_4000 = Picoscope4000()

    return picoscope_4000

def test_class_vars(picoscope_):
    print(picoscope_.OpenUnit)


def test_globals(picoscope_, sampling_params):
    picoscope_.set_globals(no_samples_=sampling_params[1])


def test_connect(picoscope_):
    picoscope_.connect()  # Assertion called implicitly in function


def test_set_channel_params(picoscope_):
    picoscope_.set_channel_params(
        enum_voltage_range=enum_voltage_range, channel=CHANNEL)


@pytest.fixture
def no_frequencies():
    no_frequencies = utils.get_no_frequencies(
        start_freq=params['start_freq'],
        end_freq=params['end_freq'],
        increment=params['increment'])

    return no_frequencies


def test_get_timebase(picoscope_, sampling_params):
    picoscope_.get_timebase(
        enum_sampling_interval=sampling_params[0])


def test_set_simple_trigger(picoscope_):
    picoscope_.set_simple_trigger(channel=CHANNEL)


def test_define_procedure(picoscope_):
    picoscope_.define_procedure(**params)


def test_set_data_buffer(picoscope_):
    picoscope_.set_data_buffer(channel=CHANNEL)


def test_run_block(picoscope_, sampling_params):
    picoscope_.run_block(enum_sampling_interval=sampling_params[0])


def test_trigger_pull(picoscope_):
    picoscope_.pull_trigger()


def test_wait_ready(picoscope_):
    picoscope_.wait_ready()


def test_get_data(picoscope_):
    picoscope_.get_data()


def test_stop(picoscope_):
    picoscope_.stop()


def test_to_mV(picoscope_):
    data_in_mV = picoscope_.to_mV(enum_voltage_range=enum_voltage_range)

    assert isinstance(data_in_mV, list)


def test_close(picoscope_):
    picoscope_.disconnect()
