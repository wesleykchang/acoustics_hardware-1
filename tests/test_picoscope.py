import json

from picoscope import picoscope

with open("tests/config.json") as f:
    params = json.load(f)

CHANNEL = 1


def test_connect():
    picoscope.connect()


def test_set_channel_params():
    picoscope._set_channel_params(enum_voltage_range=6, channel=CHANNEL)


def test_get_timebase():
    picoscope._get_timebase()


def test_set_simple_trigger():
    picoscope._set_simple_trigger(channel=CHANNEL)


def test_define_procedure():
    picoscope._define_procedure(**params)


def test_run_block():
    picoscope._run_block()


def test_wait_ready():
    picoscope._wait_ready()


def test_set_data_buffer():
    picoscope._set_data_buffer(channel=CHANNEL)


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
