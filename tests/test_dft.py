import numpy as np
import pytest

from picoscope import dft


@pytest.fixture
def frequencies(params):
    '''Gets the frequencies used in experiment's sweep.

    Args:
        start_freq (int): The starting frequency [Hz]
        end_freq (int): The ending frequency [Hz]
        increment (int): The step between frequencies [Hz]
                
    Returns:
        (np.array): All the frequencies used in frequency sweep
    '''

    start_freq = params['start_freq']
    end_freq = params['end_freq']
    increment = params['increment']
    
    no_frequencies = (end_freq - start_freq) / increment + 1

    frequencies = np.linspace(start_freq, end_freq, int(no_frequencies))

    return frequencies


@pytest.fixture
def sample_rate(params, frequencies, picodata):
    sample_rate = dft._get_sample_rate(
        no_points_per_sweep=len(picodata),
        no_frequencies=len(frequencies),
        dwell=params['dwell']
    )

    return sample_rate


def test_sample_rate(sample_rate):
    assert isinstance(sample_rate, float)


def test_is_sample_rate_adequate(sample_rate, frequencies):
    dft._is_sample_rate_adequate(
        sample_rate=sample_rate,
        max_frequency=max(frequencies)
    )


def test_inadequate_sample_rate(sample_rate):
    dft._is_sample_rate_adequate(
        sample_rate=sample_rate,
        max_frequency=1E6
    )

@pytest.fixture
def zero_padded_waves(picodata):
    zero_padded_waves = dft._zero_pad(sweep=picodata)

    return zero_padded_waves


def test_zero_pad_waves(zero_padded_waves):
    assert isinstance(zero_padded_waves, np.ndarray)


@pytest.fixture
def detrended_waves(zero_padded_waves):
    detrended_waves = dft._detrend(waves=zero_padded_waves)

    return detrended_waves


def test_detrend(detrended_waves):
    assert isinstance(detrended_waves, np.ndarray)


def test_get_fft_amps(detrended_waves):
    amps = dft._get_fft_amps(waves=detrended_waves)

    assert isinstance(amps, np.ndarray)


def test_get_fft_freq_bins(detrended_waves, sample_rate):
    freq_bins = dft._get_fft_freq_bins(
        waves=detrended_waves,
        sample_rate=sample_rate
    )

    assert isinstance(freq_bins, np.ndarray)

# Integration
def test_dft(params, picodata, frequencies):
    freq_bins, amps = dft.dft(
        waves=picodata,
        frequencies=frequencies,
        dwell=params['dwell']
    )

    assert isinstance(freq_bins, np.ndarray)
    assert isinstance(amps, np.ndarray)
