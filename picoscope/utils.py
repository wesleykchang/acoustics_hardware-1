import json
import warnings
from typing import NamedTuple


# This would probably be more concise as an enum
with open("picoscope/settings.json") as f:
    settings = json.load(f)


class RawParams(NamedTuple):
    """Incoming params format."""
    keys: str
    vals: str


class ParsedParams(NamedTuple):
    """Params ready to be passed to oscilloscope."""
    keys: str
    vals: float


def parse_incoming_params(raw_params: RawParams) -> ParsedParams:
    """Parses incoming JSON to an appropriate format.
    
    The raw incoming JSON has str-str key-value pairs.
    This is the case even if the actual value is a float. We ameliorate
    that here.

    Args:
        raw_params (RawParams): Raw incoming params,
            e.g. {'start_freq': '10.0'}.

    Returns:
        ParsedParams: Values ready to be passed to picoscope,
            e.g. {'start_freq': 10.0}
    """
    return dict([key, float(val)] for key, val in raw_params.items())


def parse_voltage_range(numerical_voltage_range: float = 0.01) -> int:
    """Parses voltage range from volts to an enumerated number value.

    Args:
        numerical_voltage_range (float, optional): A human-readable
            voltage [V]. Defaults to 0.01 (pulsing).

    Returns:
        (int): Enumerated voltage. Refer to manual or constants.py

    Raises:
        ValueError: 
    """        

    voltage_range_conversion_table = settings[
        "voltage_range_conversion_table"]

    for range_, voltage in voltage_range_conversion_table.items():
        if float(voltage) != numerical_voltage_range:
            continue

        parsed_voltage_range = range_
        break

    # Ensure voltage range was matched
    if 'parsed_voltage_range' not in locals():
        raise ValueError(
            "Passed voltage doesn\'t match conversion voltage!")

    return int(parsed_voltage_range)


def set_input_channel(params: dict = None) -> int:
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


def get_no_frequencies(start_freq: float, end_freq: float,
                       increment: float) -> int:
    """Gets the number of frequencies in sweep.

    Helper function for calculate_sampling_rate()

    Args:
        start_freq (float): Starting frequency [Hz].
        end_freq (float): Last frequency [Hz].
        increment (float): Step between each frequency in sweep [Hz].

    Returns:
        int: Number of frequencies in sweep.
    """

    if start_freq > end_freq:
        raise (ValueError,
               "End freq must be equal to or larger than start freq!")

    return (end_freq - start_freq) / increment + 1


def set_sampling_params(no_samples: int = 1e4,
                        dwell: float = 0.01,
                        no_frequencies: int = 1,
                        baseline: float = 1E-7) -> int:
    """Calculates the appropriate sampling interval and number of samples collected.

    Necessary to set GetTimebase() appropriately.

    The actual value that's passed to GetTimebase() is an enumerated value.
    1E-7 (100 ns) is 0, 2E-7 (200 ns) is 1, etc.

    Args:
        no_samples (int, optional): _Desired_ number of samples to be collected.
        dwell (float, optional): The time [s] between frequency changes when sweeping.
        no_frequencies (int, optional): Number of frequencies.
        baseline (float, optional). Fastest rated sample rate of oscilloscope.
            Generally not to be tinkered with. Defaults to 1E-7 (i.e. 100 ns).

    Returns:
        int: The **enumerated** sampling interval.
        int: _Adjusted_ number of samples to be collected.
    """

    sweep_duration = dwell * no_frequencies  # [s]
    sampling_interval = sweep_duration / no_samples  # [s]

    adjusted_no_samples = no_samples

    if sampling_interval < baseline:
        sampling_interval = baseline
        adjusted_no_samples = sweep_duration / sampling_interval
        warnings.warn(
            f'Sampling interval set smaller than baseline {int(baseline*1E9)} [ns]. ' \
            f'Changing to baseline and adjusting number of samples from {int(no_samples)} ' \
            f'to {int(adjusted_no_samples)}'
        )

    enum_sampling_interval = sampling_interval / baseline - 1

    return int(enum_sampling_interval), int(adjusted_no_samples)
