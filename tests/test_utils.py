import json
import pytest

from picoscope import utils

with open("tests/config.json") as f:
    params = json.load(f)


def test_parse_voltage_range():
    assert utils.parse_voltage_range(1) == 6


def test_parse_voltage_range_failure():
    with pytest.raises(ValueError) as e_info:
        utils.parse_voltage_range(4.9)


def test_set_default_input_channel():
    params['channel'] = utils.set_input_channel(params=params)

    assert params['channel'] == 0


def test_incorrectly_formatted_input_channel():
    params['channel'] = 'A'
    with pytest.raises(ValueError):
        utils.set_input_channel(params=params)


def test_custom_input_channel():
    del params['channel']

    params['channel'] = utils.set_input_channel(params=params)

    assert params['channel'] == 1