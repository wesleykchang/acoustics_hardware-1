"""Typically we're only connected to one picoscope at a time.
We can therefore only run part of these tests at any given time:
either the sweep tests or pulsing. The other should be commented
"""

import pickle
from picosdk.errors import PicoSDKCtypesError
import pytest
from typing import Dict, Union

from picoscope.constants import SignalProperties
from picoscope.techniques import pulse
from picoscope.picoscope import Picoscope2000


@pytest.fixture
def connection():
    picoscope_ = Picoscope2000()

    yield picoscope_.connect()

    # Teardown
    picoscope_.disconnect()

    with open('tests/data/waveform.pkl', 'wb') as f:
        pickle.dump(picodata, f)


def test_pulse(picoscope_: Picoscope2000, signal_properties: SignalProperties):

    global picodata

    picodata = pulse(picoscope_=picoscope_, params=params)

    assert isinstance(picodata, list)