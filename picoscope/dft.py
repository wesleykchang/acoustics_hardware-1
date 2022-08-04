

import numpy as np
from scipy import signal
from scipy import stats


def _detrend(waves: np.array) -> np.array:
    """Hmm

    Args:
        waves (np.array): Zero-padded waves

    Returns:
        (np.array): Detrended waves
    
    Note:
        Must be run after _zero_pad()
    """
    return signal.detrend(waves)


def _get_absolute_transform(fft: np.array) -> np.array:
    """Calculates total length of transform for complex number.

    The FFT results in complex-valued numbers.
    np.abs() calculates sqrt(a²+b²) for complex number a+bi.

    Helper function for _get_fft()

    Args:
        fft (np.array): The raw results from FFT

    Returns:
        (np.array): Length of every complex-valued number in FFT
    """
    return np.abs(fft)


def _get_fft_amps(waves: np.array) -> np.array:
    """Calculates FFT amplitudes.
    
    Args:
        waves (np.array): 2D wave array of waveforms,
            shape [no_sweeps, no_points_in_sweep].

    Returns:
        normalized_amps (np.array): 2D array of frequency powers,
            shape [no_sweeps, no_freq_bins].
    """

    amps_complex = np.fft.rfft(waves)
    amps_length = _get_absolute_transform(fft=amps_complex)
    normalized_amps = _normalize_amps(amps=amps_length)

    return normalized_amps

def _get_fft_freq_bins(waves: np.array, sample_rate: float) -> np.array:
    """_summary_

    _extended_summary_

    Args:
        waves (np.array): 2D wave array of waveforms,
            shape [no_sweeps, no_points_in_sweep].
        sample_rate (float): Sample rate [s].

    Returns:
        freq_bins (np.array): 1D array of frequency bin centers.
    """

    window_len = len(waves)
    freq_bins = np.fft.rfftfreq(n=window_len, d=1/sample_rate)

    return freq_bins



def _get_sample_rate(no_points_per_sweep: int, no_frequencies: int,
                     dwell: float) -> float:
    """Calculates sampling rate in ResoStat frequency sweep.

    Args:
        no_points_per_sweep (int): The number of data points collected
            in each sweep
        no_frequencies (int): The total number of frequencies used
            in experiment
        dwell (float): The time spent on each frequency during each sweep

    Returns:
        (float): The sampling rate [s].
    """
    return no_points_per_sweep / no_frequencies / dwell


def _is_sample_rate_adequate(sample_rate: float,
                             max_frequency: int) -> None:
    """Sanity check for FFT quality.
    
    Sample_rate must be at least twice the highest signal frequency (Nyquist).

    Args:
        sample_rate (float): The calculated sample rate,
            see _get_sample_rate()
        max_frequency (int): The highest frequency used in frequency sweep
    """

    try:
        assert sample_rate >= 2 * max_frequency
    except AssertionError:
        print("\nSample rate doesn\'t fulfill requirements.\n")


def _normalize_amps(amps: np.array) -> np.array:
    """Normalizes to simplify plotting.

    Helper function for _get_fft()
    
    Args:
        amps(np.array): Frequency amplitudes from FFT

    Note:
        Run after _get_absolute_transform()
    """
    return np.divide(amps.T, np.max(amps)).T


def _zero_pad(sweep: np.array, pad_x: int = 2) -> np.array:
    """Zero pads waves to increase FFT frequency resolution.

    Standard practice for FFTs. See e.g. https://bit.ly/3BPcG4q.

    Args:
        sweep (np.array): One sweep.
            Shape: [no_sweeps, no_points_in_sweep]
        pad_x (int): Optional. The padding multiplication factor.
            Defaults to 2.
    """

    no_points_per_sweep_padded = len(sweep) * pad_x
    z = np.zeros(no_points_per_sweep_padded, dtype='uint8')
    padded_sweep = np.concatenate((z, sweep, z),
                                  axis=0,
                                  dtype=np.float16)

    return padded_sweep


def remove_outliers_np(array: np.array,
                       z_max: float = 3.0) -> np.array:
    """Removes outliers by filtering the z-score (i.e. no of stdevs from mean).
    
    Args:
        array (np.array): Only tested on 1D arrays. If doesn't work on 2D
            then it only needs slight tweaks.
        z_max (float): Optional. Max z-score (st devs) to include when
            when removing outliers. Defaults to 3.0
    Returns:
        (np.array)
    """

    z_score = stats.zscore(array)

    return array[(np.abs(z_score) < z_max)]


def dft(waves: np.array, frequencies: list, dwell: float, pad_x: int = 2) -> list([np.array, np.array]):
    """Wrapper for the Discrete Fourier Transform.

    Violently violates the single responsibility principle.

    Args:
        waveform (np.array): Raw waveform.
        frequencies (list): All frequencies featured in sweep.
        dwell (float): Duration per frequency in sweep.
        pad_x (int, optinal): Padding factor. Increases DFT resolution.
            Defaults to 2.

    Returns:
        np.array: frequency bins.
        np.array: Fourier transform powers by frequency in frequency bin.
    """

    sample_rate = _get_sample_rate(
        no_points_per_sweep=len(waves),
        no_frequencies=len(frequencies),
        dwell=dwell)
    _is_sample_rate_adequate(
        sample_rate=sample_rate,
        max_frequency=max(frequencies)
    )

    padded_waves = _zero_pad(sweep=waves, pad_x=pad_x)
    padded_waves = padded_waves[~np.isnan(padded_waves)]
    detrended_waves = _detrend(waves=padded_waves)  # remove
    # detrended_waves_wo_outliers = remove_outliers_np(
        # detrended_waves)

    amps = _get_fft_amps(
        waves=detrended_waves
    )
    freq_bins = _get_fft_freq_bins(
        waves=detrended_waves,
        sample_rate=sample_rate
    )

    return freq_bins, amps