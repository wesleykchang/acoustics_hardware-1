import json

def parse_voltage_range(numerical_voltage_range) -> float:
    """Parses voltage range from volts to a categorical number value.

    Args:
        numerical_voltage_range (float): 

    Returns:
        (float)

    Raises:
        ValueError: 
    """

    with open("settings.json") as f:
        settings = json.load(f)
    voltage_range_conversion_table = settings["voltage_range_conversion_table"]

    for range_, voltage in voltage_range_conversion_table.values():
        if voltage == numerical_voltage_range:
            parsed_voltage_range = range_
            break

    # Ensure voltage range was matched
    if 'parsed_voltage_range' not in locals():
        raise ValueError("Passed voltage doesn\'t match conversion volta")

    return float(parsed_voltage_range)

def set_sample_rate(end_freq: float):
    """

    Args:
        INCOMPLETE
        end_freq (float): Highest frequency to be "played" in sweep [Hz]

    Returns:
        sample_rate (float): Sampling rate [Hz]
    
    Raises:
        ValueError: If sample rate is less than the Nyquist frequency.
    """

    if end_freq != None:
        if end_freq > sample_rate*2:
            raise ValueError("Sample rate is less than Nyquist frequency!")

    return sample_rate
