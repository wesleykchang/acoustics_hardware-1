"""Typically we're only connected to one picoscope at a time.
We can therefore only run part of these tests at any given time:
either the sweep tests or pulsing. The other should be commented
"""

import matplotlib.pyplot as plt
import numpy as np
import pickle
import pytest

from picoscope.parameters import PulsingParams
from picoscope.picoscope import Picoscope2000
from picoscope import pulse

COL = 'amps'

pulsing_params: PulsingParams = PulsingParams(
    delay = 26,
    voltage_range = 1,
    duration = 8
)

@pytest.fixture
def instance():
    picoscope_ = Picoscope2000()

    return picoscope_

@pytest.fixture
def connection(instance: Picoscope2000):
    instance.connect()

    yield instance

    # Teardown
    instance.disconnect()

    with open('tests/data/waveform.pkl', 'wb') as f:
        pickle.dump(waveform, f)


def test_pulse(connection: Picoscope2000):
    global waveform

    waveform = pulse.pulse(
        picoscope_=connection,
        pulsing_params=pulsing_params
    )

    assert isinstance(waveform, dict)
    assert isinstance(waveform[COL], list)
    assert isinstance(waveform[COL][0], float)
    assert np.mean(abs(np.asarray(waveform[COL])) > 0)

    plt.plot()


def test_pulse_wo_connection(instance: Picoscope2000):
    global waveform

    waveform = pulse.pulse(
        picoscope_=instance,
        pulsing_params=pulsing_params
    )

    assert isinstance(waveform, dict)
    assert isinstance(waveform[COL], list)
    assert isinstance(waveform[COL][0], float)
    assert np.mean(abs(np.asarray(waveform[COL])) > 0)
