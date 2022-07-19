import json
from picosdk.errors import PicoSDKCtypesError
import pytest

from picoscope import picoscope, sweep

with open("tests/config.json") as f:
    params = json.load(f)

samples_max = int(1E4)


@pytest.fixture
def connection():
    picoscope.connect()


def test_unsuccessful_sweep_no_connection():
    """Fails because a picoscope connection isn't established."""

    with pytest.raises(PicoSDKCtypesError):
        sweep.sweep(params=params)


def test_successful_sweep(connection):
    """Succeeds as it inherits a picoscope connection."""

    resonance_data = sweep.sweep(params=params)

    assert isinstance(resonance_data, list)
