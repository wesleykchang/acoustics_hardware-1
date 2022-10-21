"""Typically we're only connected to one picoscope at a time.
We can therefore only run part of these tests at any given time:
either the sweep tests or pulsing. The other should be commented
"""

import pickle
from picosdk.errors import PicoSDKCtypesError
import pytest
from typing import Union

from picoscope.techniques import pulse, sweep
from picoscope.picoscope import Picoscope2000, Picoscope4000


@pytest.fixture
def connection():
    picoscope_ = Picoscope2000()

    yield picoscope_.connect()

    # Teardown
    picoscope_.disconnect()

    with open('tests/data/waveform.pkl', 'wb') as f:
        pickle.dump(picodata, f)


### SWEEP


def test_unsuccessful_sweep_no_connection(params: dict[str:Union[float, int]]):
    """Fails because a picoscope connection isn't established."""

    with pytest.raises(PicoSDKCtypesError):
        sweep(params=params)


def test_successful_sweep(picoscope_: Picoscope4000,
                          params: dict[str:Union[float, int]]):
    """Succeeds as it inherits a picoscope connection."""

    global picodata

    picodata = sweep(picoscope_=picoscope_, params=params)

    assert isinstance(picodata, list)


### PULSE


def test_pulse(picoscope_: Picoscope2000, params: dict[str:Union[float, int]]):

    global picodata

    picodata = pulse(picoscope_=picoscope_, params=params)

    assert isinstance(picodata, list)