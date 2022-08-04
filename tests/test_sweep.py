import pickle
from picosdk.errors import PicoSDKCtypesError
import pytest

from picoscope import picoscope, sweep


def test_unsuccessful_sweep_no_connection(params):
    """Fails because a picoscope connection isn't established."""

    with pytest.raises(PicoSDKCtypesError):
        sweep.sweep(params=params)


@pytest.fixture
def connection():
    yield picoscope.connect()

    # Teardown
    with open('tests/data/waveform.pkl', 'wb') as f:
        pickle.dump(picodata, f)


def test_successful_sweep(params, connection):
    """Succeeds as it inherits a picoscope connection."""

    global picodata
    picodata = sweep.sweep(params=params)

    assert isinstance(picodata, list)
