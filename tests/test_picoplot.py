import numpy as np
import pytest

from picoscope import dft, picoplot


@pytest.fixture
def duration(params):
    """Calculates sweep duration.
    
    Args:
        start_freq (int): Lowest frequency [Hz].
        end_freq (int): Highest frequency [Hz].
        increment (int): Step size between frequencies in sweep [Hz].
        dwell (float): How long each frequency is swept at [s].
        
    Returns:
        float: How long sweep takes [s].
    """

    return ((params['end_freq'] - params['start_freq']) //
            params['increment'] + 1) * params['dwell']


@pytest.fixture
def frequencies(params):
    frequencies = np.arange(
        params['start_freq'],
        params['end_freq']+params['increment'],
        params['increment']
    )

    return frequencies


@pytest.fixture
def dft_(frequencies, picodata, params):
    freq_bins, amps = dft.dft(
        waves=picodata,
        frequencies=frequencies,
        dwell=params['dwell']
    )

    return freq_bins, amps


def test_figure(params, picodata, duration, frequencies, dft_):
    fig = picoplot.Picoplot()
    fig.plot_waveform(wave=picodata, duration=duration)
    fig.freq_step(frequencies=frequencies, dwell=params['dwell'])
    fig.plot_params(params=params)
    fig.plot_dft(freq_bins=dft_[0], amps=dft_[1])
    status = fig.save()

    assert status == 'figure saved'