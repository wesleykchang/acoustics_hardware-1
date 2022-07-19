import json


def parse_voltage_range(numerical_voltage_range: float) -> int:
    """Parses voltage range from volts to a categorical number value.

    Args:
        numerical_voltage_range (float): 

    Returns:
        (int)

    Raises:
        ValueError: 
    """

    # This would probably be more concise as an enum
    with open("picoscope/settings.json") as f:
        settings = json.load(f)

    voltage_range_conversion_table = settings["voltage_range_conversion_table"]

    for range_, voltage in voltage_range_conversion_table.items():
        if float(voltage) == numerical_voltage_range:
            parsed_voltage_range = range_
            break

    # Ensure voltage range was matched
    if 'parsed_voltage_range' not in locals():
        raise ValueError("Passed voltage doesn\'t match conversion voltage!")

    return int(parsed_voltage_range)


def set_input_channel(params: dict):
    """Sets the physical input channel, either 0 (A) or 1 (B).

    The lazy parsing of params in app/get_resonance makes channel
    a float instead of int. So it either returns 1 if it's not
    specified in the input, or int(float(channel)).
    
    Args:
        params (dict): All sweep parameters. See settings.json.

    Returns:
        channel (int): Enum of the channel.
    """

    return int(params['channel']) if 'channel' in params else 1
