import numpy as np
import pytest

from picoscope.parameters import PulsingParams, builtin_voltage_ranges
from picoscope import utils

no_frequencies_reference = 10
enum_sampling_interval_reference = 0
no_samples_reference = 1E5

DELAY = 10
VOLTAGE = 1
DURATION = 8

pulsing_params_dict_int = {
    'delay': DELAY,
    'voltage_range': VOLTAGE,
    'duration': DURATION
}

dict_w_vals_as_str = dict([key, str(val)] for key, val in pulsing_params_dict_int.items())

PulsingParamsReference = PulsingParams(
    delay=DELAY,
    voltage_range=VOLTAGE,
    duration=DURATION,
)

def test_bool_to_requests_true():
    bool_str = utils.bool_to_requests(bool_=True)

    assert bool_str == '1'


def test_bool_to_requests_false():
    bool_str = utils.bool_to_requests(bool_=False)

    assert bool_str == '0'

def test_dataclass_from_dict():
    PulsingParams_ = utils.dataclass_from_dict(
        dataclass_=PulsingParams,
        dict_=pulsing_params_dict_int
    )

    assert PulsingParams_ == PulsingParamsReference


def test_parse_dict_vals_to_int():
    dict_w_vals_as_float = utils.parse_dict_vals_to_int(dict_=dict_w_vals_as_str)

    assert isinstance(dict_w_vals_as_float['delay'], int)


def test_parse_payload():
    key: str = 'amps'
    payload = utils.parse_payload(field=np.array([[0.1, 0.01], [0.08, 0.02]]), key=key)

    assert isinstance(payload, dict)
    assert isinstance(payload[key], list)
    assert isinstance(payload[key][0], float)


def test_to_enum():
    enum_ = utils.to_enum(val=9, arr_fn=builtin_voltage_ranges)
    
    assert isinstance(enum_, int)