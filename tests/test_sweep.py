import json
import numpy as np
import pickle
from picosdk.errors import PicoSDKCtypesError
import pytest

from picoscope import dft, picoplot, picoscope, sweep

with open("tests/params.json") as f:
    params = json.load(f)

start_freq = params['start_freq']
end_freq = params['end_freq']
increment = params['increment']
dwell = params['dwell']


def test_unsuccessful_sweep_no_connection():
    """Fails because a picoscope connection isn't established."""

    with pytest.raises(PicoSDKCtypesError):
        sweep.sweep(params=params)


@pytest.fixture
def duration():
    """Calculates sweep duration.
    
    Args:
        start_freq (int): Lowest frequency [Hz].
        end_freq (int): Highest frequency [Hz].
        increment (int): Step size between frequencies in sweep [Hz].
        dwell (float): How long each frequency is swept at [s].
        
    Returns:
        float: How long sweep takes [s].
    """

    return ((end_freq - start_freq) // increment + 1) * dwell


@pytest.fixture
def connection(duration):
    yield picoscope.connect()

    # Teardown
    plot_sweep(picodata=picodata, duration=duration)


def test_successful_sweep(connection):
    """Succeeds as it inherits a picoscope connection."""

    global picodata
    picodata = sweep.sweep(params=params)

    assert isinstance(picodata, list)


def plot_sweep(picodata, duration):
    with open('tests/data/waveform', 'wb') as f:
        pickle.dump(picodata, f)

    frequencies = np.arange(start_freq, end_freq+increment, increment)
    freq_bins, amps = dft.dft(
        waves=picodata,
        frequencies=frequencies,
        dwell=dwell
    )
    fig = picoplot.Picoplot()
    fig.plot_waveform(wave=picodata, duration=duration)
    fig.freq_step(frequencies=frequencies, dwell=dwell)
    fig.plot_params(params=params)
    fig.plot_dft(freq_bins=freq_bins, amps=amps)
    fig.save()