"""Typically we're only connected to one picoscope at a time.
We can therefore only run part of these tests at any given time:
either the sweep tests or pulsing. The other should be commented
"""

import numpy as np
import pickle
import pytest

from picoscope.constants import PulsingParams
from picoscope.picoscope import Picoscope2000
from picoscope.techniques import pulse

pulsing_params: PulsingParams = PulsingParams(
    delay = 26,
    voltage = 1,
    duration = 8,
    avg_num = 32
)


@pytest.fixture
def connection():
    picoscope_ = Picoscope2000()
    picoscope_.connect()

    yield picoscope_

    # Teardown
    picoscope_.disconnect()

    # with open('tests/data/waveform.pkl', 'wb') as f:
    #     pickle.dump(picodata, f)


def test_pulse(connection: Picoscope2000):
    global picodata

    picodata = pulse(picoscope_=connection, pulsing_params=pulsing_params)
    print(picodata)
    assert isinstance(picodata, dict)
    assert isinstance(picodata['amps'], list)
    assert np.mean(abs(np.asarray(picodata['amps'])) > 0)