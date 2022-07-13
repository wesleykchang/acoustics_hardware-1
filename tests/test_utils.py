import pytest

from picoscope import utils

def test_parse_voltage_range():
    assert utils.parse_voltage_range(1) == 6
    
def test_parse_voltage_range_failure():
    with pytest.raises(ValueError) as e_info:
        utils.parse_voltage_range(4.9)

# def test_set_sample_rate():
#     pass