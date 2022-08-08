from enum import Enum, auto
import json
import warnings


class AutoEnum(Enum):
    """Zero-based auto enum because I do be specific like that."""

    def _generate_next_value_(name, start, count, last_values):
        if len(last_values) > 0:
            return last_values[-1] + 1
        return 0


class SweepType(AutoEnum):
    UP = auto()
    DOWN = auto()
    UPDOWN = auto()
    DOWNUP = auto()

class ThresholdDirection(AutoEnum):
    ABOVE = auto()
    BELOW = auto()
    RISING = auto()
    FALLING = auto()
    RISING_OR_FALLING = auto()


class TriggerSource(AutoEnum):
    SIGGEN_NONE = auto()
    SIGGEN_SCOPE_TRIG = auto()
    SIGGEN_AUX_IN = auto()
    SIGGEN_EXT_IN = auto()
    SIGGEN_SOFT_TRIG = auto()


class TriggerType(AutoEnum):
    RISING = auto()
    FALLING = auto()
    GATE_HIGH = auto()
    GATE_LOW = auto()
    TRIG_TYPE = auto()


class WaveType(AutoEnum):
    SINE = auto()
    SQUARE = auto()
    TRIANGLE = auto()
    RAMP_UP = auto()
    RAMP_DOWN = auto()
    SINC = auto()
    GAUSSIAN = auto()
    HALF_SINE = auto()


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

    voltage_range_conversion_table = settings[
        "voltage_range_conversion_table"]

    for range_, voltage in voltage_range_conversion_table.items():
        if float(voltage) == numerical_voltage_range:
            parsed_voltage_range = range_
            break

    # Ensure voltage range was matched
    if 'parsed_voltage_range' not in locals():
        raise ValueError(
            "Passed voltage doesn\'t match conversion voltage!")

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


def calculate_sampling_interval(max_samples: int, dwell: float,
                                no_frequencies: int) -> int:
    """Calculates the appropriate sampling interval.

    Necessary to set GetTimebase() appropriately.

    The actual value that's passed to GetTimebase() is an enumerated value.
    1E-7 (100 ns) is 0, 2E-7 (200 ns) is 1, etc.

    Args:
        max_samples (int): Maximum number of samples to be collected.
        dwell (float): The time [s] between frequency changes.
        no_frequencies (int): Number of frequencies in sweep.

    Returns:
        int: The **enumerated** sampling interval.
    """

    baseline = 1E-7  # s

    sweep_duration = dwell * no_frequencies  # [s]
    sampling_interval = sweep_duration / max_samples  # [s]

    if sampling_interval < baseline:
        sampling_interval = baseline
        warnings.warn(f'Sampling interval set smaller than baseline {int(baseline*1E9)} [ns]. Changing to min val')
    enum_sampling_interval = sampling_interval / baseline - 1

    return int(enum_sampling_interval)
