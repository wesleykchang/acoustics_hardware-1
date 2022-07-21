import json

from picoscope import picoscope

with open("tests/config.json") as f:
    params = json.load(f)

CHANNEL = 1
enum_sampling_rate = 9

def test_connect():
    picoscope.connect()


def test_set_globals():
    picoscope.set_globals(samples_max=params['max_samples'])


def test_set_channel_params():
    picoscope.set_channel_params(enum_voltage_range=6, channel=CHANNEL)


def test_get_timebase():
    picoscope.get_timebase(enum_sampling_rate=enum_sampling_rate)


def test_set_simple_trigger():
    picoscope.set_simple_trigger(channel=CHANNEL)


def test_define_procedure():
    picoscope.define_procedure(**params)


def test_run_block():
    picoscope.run_block(enum_sampling_rate=enum_sampling_rate)


def test_trigger_pull():
    picoscope.pull_trigger()


def test_wait_ready():
    picoscope.wait_ready()


def test_set_data_buffer():
    picoscope.set_data_buffer(channel=CHANNEL)


def test_get_data():
    picoscope.get_data()


def test_teardown():
    picoscope.teardown()


def test_stop():
    picoscope.stop()


def test_to_mV():
    data_in_mV = picoscope.to_mV(enum_voltage_range=1)

    assert isinstance(data_in_mV, list)


def test_close():
    picoscope.close()
