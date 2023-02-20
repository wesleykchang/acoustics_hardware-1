import json
import pytest

from picoscope.constants import PulsingParams
from picoscope import utils

no_frequencies_reference = 10
enum_sampling_interval_reference = 0
no_samples_reference = 1E5

DELAY = 10
VOLTAGE = 1
DURATION = 8
AVG_NUM = 1024

voltage_ranges = [2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1., 2., 5., 10., 20.]


pulsing_params_dict_int = {
    'delay': DELAY,
    'voltage': VOLTAGE,
    'duration': DURATION,
    'avg_num': AVG_NUM
}
pulsing_params_dict_str = {k : str(v) for k, v in pulsing_params_dict_int.items()}

PulsingParamsReference = PulsingParams(
    delay=DELAY,
    voltage=VOLTAGE,
    duration=DURATION,
    avg_num=AVG_NUM
)

def test_dataclass_from_dict():
    PulsingParams_ = utils.dataclass_from_dict(
        dataclass_=PulsingParams,
        dict_=pulsing_params_dict_int
    )

    assert PulsingParams_ == PulsingParamsReference


def test_parse_incoming_params():
    PulsingParams_ = utils.parse_incoming_params(raw_params=pulsing_params_dict_str)

    assert PulsingParams_ == PulsingParamsReference


def test_parse_voltage():
    for enumeration, voltage_range in enumerate(voltage_ranges):
        enumerated_voltage = utils.parse_voltage(voltage=voltage_range)
        
        assert enumerated_voltage == enumeration


# def test_find_nearest_enum():


def test_parse_sampling_interval():
    enum_sampling_interval = utils.parse_sampling_interval(sampling_interval=2e-9)