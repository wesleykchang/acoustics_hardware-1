import json
import pytest
from typing import Tuple

from picoscope.constants import TriggerProperties
from picoscope.picoscope import Picoscope2000

with open("tests/params.json") as f:
    params = json.load(f)

CHANNEL = 1
ENUM_VOLTAGE_RANGE = 6


@pytest.fixture
def sampling_params():

    return 8, 0


@pytest.fixture
def picoscope_():    
    picoscope_ = Picoscope2000()

    yield picoscope_

    # Teardown
    picoscope_.disconnect()


def test_connect(picoscope_: Picoscope2000):
    picoscope_.connect()  # Assertion called implicitly in function


@pytest.fixture
def connection_wo_n_samples_set(picoscope_: Picoscope2000):
    picoscope_.connect()  # Assertion called implicitly in function

    return picoscope_


def test_set_n_samples_not_set(connection_wo_n_samples_set: Picoscope2000):
    n_samples_should_be_none = connection_wo_n_samples_set.n_samples

    assert n_samples_should_be_none == None


def test_set_n_samples_set(connection_wo_n_samples_set: Picoscope2000):

    connection_wo_n_samples_set.set_n_samples(duration=6)
    n_samples = connection_wo_n_samples_set.n_samples

    assert n_samples == 3000    


@pytest.fixture
def connection(picoscope_: Picoscope2000):

    picoscope_.connect()  # Assertion called implicitly in function
    picoscope_.set_n_samples(duration=6)
    picoscope_.set_segment_index(segment=0)

    return picoscope_


def test_is_connected(connection: Picoscope2000):
    is_connected = connection.is_connected()

    assert is_connected

def test_is_not_connected():
    picoscope_ = Picoscope2000()
    is_connected = picoscope_.is_connected()

    assert is_connected == False


def test_get_analogue_offset(connection: Picoscope2000):
    for i in range(1, 10):
        max_voltage = connection.get_analogue_offset(voltage=i)

        assert isinstance(max_voltage, float)


def test_set_channel(connection: Picoscope2000):
    connection.set_channel(enum_voltage_range=5)


def test_get_timebase(connection: Picoscope2000):
    connection.check_timebase()


@pytest.fixture
def trigger_properties():

    trigger_properties = TriggerProperties()

    trigger_properties.set_delay(
        delay_us=6,
        sampling_interval=2e-9
    )

    return trigger_properties

def test_set_simple_trigger(connection: Picoscope2000, trigger_properties: TriggerProperties):
    connection.set_simple_trigger(trigger_properties=trigger_properties)


def test_setup_signal(connection: Picoscope2000):
    connection.setup_signal()


@pytest.fixture
def buffer(picoscope_: Picoscope2000):
    buffer = picoscope_.make_buffer()

    return buffer
    

def test_set_data_buffer(connection: Picoscope2000, buffer):
    connection.set_data_buffer(c_buffer=buffer)


def test_set_averaging(connection: Picoscope2000):
    connection.set_averaging(avg_num=32)


def test_run_block(connection: Picoscope2000, sampling_params: Tuple[int, int]):
    connection.run_block(enum_sampling_interval=sampling_params[0])


def test_pull_trigger(connection: Picoscope2000):
    connection.pull_trigger()


def test_wait_ready(connection: Picoscope2000):
    connection.wait_ready()


def test_get_data(connection: Picoscope2000):
    connection.get_data()


def test_stop(connection: Picoscope2000):
    connection.stop()


def test_to_mV(connection: Picoscope2000, buffer):
    data_in_mV = connection.to_mV(
        enum_voltage_range=ENUM_VOLTAGE_RANGE,
        c_buffer=buffer
    )
    print(data_in_mV)

    assert isinstance(data_in_mV, list)


def test_close():
    picoscope_ = Picoscope2000()
    picoscope_.connect()
    picoscope_.disconnect()
