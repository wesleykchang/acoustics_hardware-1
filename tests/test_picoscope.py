import json
import pytest
from typing import Tuple

from picoscope.constants import Channel, SignalProperties, TriggerProperties
from picoscope import utils
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


@pytest.fixture
def connection(picoscope_: Picoscope2000):

    picoscope_.connect()  # Assertion called implicitly in function

    return picoscope_


def test_connect(picoscope_: Picoscope2000):
    picoscope_.connect()  # Assertion called implicitly in function


# def test_class_vars(picoscope_: Picoscope2000):
#     print(picoscope_.OpenUnit)


def test_get_analogue_offset(connection: Picoscope2000):
    for i in range(1, 10):
        max_voltage = connection.get_analogue_offset(voltage=i)

        assert isinstance(max_voltage, float)


def test_set_channel(connection: Picoscope2000):
    connection.set_channel(
        voltage=5,
        analog_offset=0
    )


def test_get_timebase(connection: Picoscope2000):
    connection.check_timebase(timebase=1)


def test_set_simple_trigger(connection: Picoscope2000):
    connection.set_simple_trigger()


def test_define_procedure(connection: Picoscope2000):
    connection.define_procedure(signal_properties=SignalProperties())


@pytest.fixture
def buffer(picoscope_: Picoscope2000):
    buffer = picoscope_.make_buffer()

    return buffer
    

def test_set_data_buffer(connection: Picoscope2000, buffer):
    connection.set_data_buffer(c_buffer=buffer)


def test_run_block(connection: Picoscope2000, sampling_params: Tuple[int, int]):
    connection.run_block(enum_sampling_interval=sampling_params[0])


def test_trigger_pull(connection: Picoscope2000):
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

    assert isinstance(data_in_mV, list)


def test_close(connection: Picoscope2000):
    connection.disconnect()
