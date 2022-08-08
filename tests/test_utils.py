import json
import pytest

from picoscope import utils

no_frequencies_reference = 10
enum_sampling_interval_reference = 0
no_samples_reference = 1E5


def test_parse_voltage_range():
    assert utils.parse_voltage_range(1) == 6


def test_parse_voltage_range_failure():
    with pytest.raises(ValueError):
        utils.parse_voltage_range(4.9)


def test_set_default_input_channel(params):
    params['channel'] = utils.set_input_channel(params=params)

    assert params['channel'] == 1


def test_incorrectly_formatted_input_channel(params):
    params['channel'] = 'A'
    with pytest.raises(ValueError):
        utils.set_input_channel(params=params)


def test_custom_input_channel(params):
    del params['channel']

    params['channel'] = utils.set_input_channel(params=params)

    assert params['channel'] == 1


@pytest.fixture
def no_freqs(params):
    no_freqs = utils.get_no_frequencies(
        start_freq=params['start_freq'],
        end_freq=params['end_freq'],
        increment=params['increment'])

    return no_freqs


def test_get_no_frequencies(no_freqs):
    assert no_freqs == no_frequencies_reference


def test_sampling_interval_calculation(params, no_freqs):
    enum_sampling_interval, _ = utils.set_sampling_params(
        no_samples=params['max_samples'],
        dwell=params['dwell'],
        no_frequencies=no_freqs,
    )

    assert enum_sampling_interval == enum_sampling_interval_reference


def test_no_samples_adjusted(params, no_freqs):
    _, no_samples = utils.set_sampling_params(
        no_samples=params['max_samples'],
        dwell=params['dwell'],
        no_frequencies=no_freqs,
    )

    assert no_samples == int(no_samples_reference)