import numpy as np
import pickle
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


def test_figure(params, picodata, duration):
    frequencies = np.arange(params['start_freq'], params['end_freq']+params['increment'], params['increment'])
    freq_bins, amps = dft.dft(
        waves=picodata,
        frequencies=frequencies,
        dwell=params['dwell']
    )
    fig = picoplot.Picoplot()
    fig.plot_waveform(wave=picodata, duration=duration)
    fig.freq_step(frequencies=frequencies, dwell=params['dwell'])
    fig.plot_params(params=params)
    fig.plot_dft(freq_bins=freq_bins, amps=amps)
    status = fig.save()

    assert status == 'figure saved'