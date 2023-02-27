import pytest

from picoscope.picoscope import Picoscope2000

CHANNEL: int = 1
VOLTAGE_RANGE: int = 6
ENUM_VOLTAGE_RANGE = 7
N_SAMPLES: int = 3000
DURATION: int = 6
DELAY_IN_US: int = 10
DELAY_IN_SAMPLES: int = 5000
DUMMY_SEGMENT_INDEX: int = 20


@pytest.fixture
def picoscope_():    
    picoscope_ = Picoscope2000()

    return picoscope_

def test_set_n_samples_not_set(picoscope_: Picoscope2000):
    n_samples_should_be_none = picoscope_.n_samples

    assert n_samples_should_be_none is None


def test_set_n_samples_set(picoscope_: Picoscope2000):
    picoscope_.n_samples = DURATION
    n_samples = picoscope_.n_samples

    assert n_samples == N_SAMPLES    


def test_enum_voltage_range_not_set(picoscope_: Picoscope2000):
    enum_voltage_range_should_be_none = picoscope_.enum_voltage_range

    assert enum_voltage_range_should_be_none is None


def test_enum_voltage_range(picoscope_: Picoscope2000):
    picoscope_.enum_voltage_range = VOLTAGE_RANGE
    enum_voltage_range = picoscope_.enum_voltage_range

    assert enum_voltage_range == ENUM_VOLTAGE_RANGE


def test_trigger_properties_delay_not_set(picoscope_: Picoscope2000):
    trigger_properties = picoscope_.trigger_properties
    delay_should_be_none = trigger_properties.delay

    assert delay_should_be_none is None


def test_trigger_properties_delay_set(picoscope_: Picoscope2000):
    picoscope_.trigger_properties = DELAY_IN_US
    trigger_properties = picoscope_.trigger_properties

    assert trigger_properties.delay == DELAY_IN_SAMPLES


def test_segment_index_initial_value_should_be_zero(picoscope_: Picoscope2000):
    segment_index = picoscope_.segment_index

    assert segment_index == 0


def test_segment_index(picoscope_: Picoscope2000):
    picoscope_.segment_index = DUMMY_SEGMENT_INDEX
    segment_index = picoscope_.segment_index

    assert segment_index == DUMMY_SEGMENT_INDEX


@pytest.fixture
def setup_for_connect(picoscope_: Picoscope2000):
    yield picoscope_

    picoscope_.disconnect()


def test_connect(setup_for_connect: Picoscope2000):
    setup_for_connect.connect()  # Assertion called implicitly in function


def test_is_not_connected(picoscope_: Picoscope2000):
    is_connected = picoscope_.is_connected

    assert is_connected == False


@pytest.fixture
def connection(picoscope_: Picoscope2000):

    picoscope_.connect()
    picoscope_.n_samples = DURATION
    picoscope_.segment_index = 0
    picoscope_.enum_voltage_range = VOLTAGE_RANGE
    picoscope_.trigger_properties = DELAY_IN_US

    yield picoscope_

    picoscope_.disconnect()


def test_is_connected(connection: Picoscope2000):
    is_connected = connection.is_connected

    assert is_connected


def test_set_channel(connection: Picoscope2000):
    connection.set_channel()


def test_check_timebase(connection: Picoscope2000):
    connection.check_timebase()


def test_set_simple_trigger(connection: Picoscope2000):
    connection.set_trigger()


def test_buffer_is_not_made(connection: Picoscope2000):
    assert connection._c_buffer is None


@pytest.fixture
def connection_w_buffer(connection: Picoscope2000):
    connection.set_buffer()

    return connection
    

def test_set_averaging(connection_w_buffer: Picoscope2000):
    connection_w_buffer.set_averaging()


def test_run_block(connection_w_buffer: Picoscope2000):
    connection_w_buffer.run_block()


def test_pull_trigger(connection_w_buffer: Picoscope2000):
    connection_w_buffer.pull_trigger()


# Not running these two bc they can't be run as unit tests w/o a lot of overhead
# Are run implicitly in intergration tests (see test_pulse.py and test_app.py)
# def test_wait_ready(connection_w_buffer: Picoscope2000):
#     connection_w_buffer.wait_ready()


# def test_get_data(connection_w_buffer: Picoscope2000):
#     connection_w_buffer.get_data()


def test_stop(connection_w_buffer: Picoscope2000):
    connection_w_buffer.stop()


def test_to_mV(connection_w_buffer: Picoscope2000):
    data_in_mV = connection_w_buffer.to_mV()

    assert isinstance(data_in_mV, list)
    assert isinstance(data_in_mV[0], float)


@pytest.fixture
def setup_for_close(picoscope_: Picoscope2000):
    picoscope_.connect()

    return picoscope_


def test_close(setup_for_close: Picoscope2000):
    setup_for_close.disconnect()
