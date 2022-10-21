import json
import pytest
from typing import Union

from picoscope import utils
from picoscope.picoscope import Picoscope2000, Picoscope4000

with open("tests/params.json") as f:
    params = json.load(f)

CHANNEL = 1
ENUM_VOLTAGE_RANGE = 6


@pytest.fixture
def sampling_params(no_frequencies):
    enum_sampling_interval, no_samples = utils.set_sampling_params(
        no_samples=params['max_samples'],
        dwell=params['dwell'],
        no_frequencies=no_frequencies)

    return enum_sampling_interval, no_samples


@pytest.fixture
def picoscope_():
    """Manually toggle between the two, depending on picoscope connected."""
    
    picoscope_ = Picoscope4000()
    # picoscope_ = Picoscope2000()

    return picoscope_

def test_class_vars(picoscope_: Union[Picoscope2000, Picoscope4000]):
    print(picoscope_.OpenUnit)


def test_connect(picoscope_: Union[Picoscope2000, Picoscope4000]):
    picoscope_.connect()  # Assertion called implicitly in function


def test_set_channel_params(picoscope_: Union[Picoscope2000, Picoscope4000]):
    picoscope_.set_channel_params(
        enum_voltage_range=ENUM_VOLTAGE_RANGE, channel=CHANNEL)


@pytest.fixture
def no_frequencies():
    no_frequencies = utils.get_no_frequencies(
        start_freq=params['start_freq'],
        end_freq=params['end_freq'],
        increment=params['increment'])

    return no_frequencies


def test_get_timebase(picoscope_: Union[Picoscope2000, Picoscope4000], sampling_params: tuple[int, int]):
    picoscope_.get_timebase(
        enum_sampling_interval=sampling_params[0])


def test_set_simple_trigger(picoscope_: Union[Picoscope2000, Picoscope4000]):
    picoscope_.set_simple_trigger(channel=CHANNEL)


def test_define_procedure(picoscope_: Union[Picoscope2000, Picoscope4000]):
    picoscope_.define_procedure(**params)


def test_set_data_buffer(picoscope_: Union[Picoscope2000, Picoscope4000]):
    picoscope_.set_data_buffer(channel=CHANNEL)


def test_run_block(picoscope_: Union[Picoscope2000, Picoscope4000], sampling_params: tuple[int, int]):
    picoscope_.run_block(enum_sampling_interval=sampling_params[0])


def test_trigger_pull(picoscope_: Union[Picoscope2000, Picoscope4000]):
    picoscope_.pull_trigger()


def test_wait_ready(picoscope_: Union[Picoscope2000, Picoscope4000]):
    picoscope_.wait_ready()


def test_get_data(picoscope_: Union[Picoscope2000, Picoscope4000]):
    picoscope_.get_data()


def test_stop(picoscope_: Union[Picoscope2000, Picoscope4000]):
    picoscope_.stop()


def test_to_mV(picoscope_: Union[Picoscope2000, Picoscope4000]):
    data_in_mV = picoscope_.to_mV(enum_voltage_range=ENUM_VOLTAGE_RANGE)

    assert isinstance(data_in_mV, list)


def test_close(picoscope_: Union[Picoscope2000, Picoscope4000]):
    picoscope_.disconnect()
