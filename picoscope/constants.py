from dataclasses import dataclass
import numpy as np
from enum import Enum, auto


MAX_SAMPLING_RATE = 1e9


def get_builtin_voltage_ranges():
    """The builtin voltage ranges"""
    return np.asarray([2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1., 2., 5., 10., 20.])


def get_available_sampling_intervals():
    return 2**np.arange(0, 1000) / MAX_SAMPLING_RATE

class AutoEnum(Enum):
    """Zero-based auto enum because I do be specific like that."""

    def _generate_next_value_(name, start, count, last_values):
        if len(last_values) > 0:
            return last_values[-1] + 1
        return 0

class Channel(AutoEnum):
    A = auto()
    B = auto()
    C = auto()
    D = auto()


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


@dataclass
class PulsingParams:
    """All the params that should should be passed
    to a pulsing picoscope, no more, no less.
    """

    delay: int
    voltage: int
    duration: int
    avg_num: int


@dataclass
class SignalProperties:
    """
    Attributes:
        offset_voltage (int): The voltage offset [uV].
            Defaults to 0.
        pk_to_pk (int): Peak-to-peak voltage [uV].
            Defaults to 2E6.
        wave_type (str): The type of waveform to be generated.
            Refer to programmer's guide for all available types.
            Defaults to 'Sine'.
        start_freq (float): Starting frequency.
            Defaults to 1.0E6.
        end_freq (float): Stopping (or reversing) frequency (included).
            Defaults to None.
        increment (float): The amount by which the frequency rises (or falls).
            Defaults to 10.0.
        dwell_time (float): The time [s] between frequency changes.
            Defaults to 1E-3.
        dwell_time (str): Determines sweeping type.
            Refer to programmer's guide for all available types.
            Defaults to 'UP'.
        shots (int): The number of cycles of the waveform to be produced
            after a trigger event. Defaults to 1.
        sweeps (int): Number of sweep repetitions.
            Defaults to 0.
        trigger_type (str): The type of trigger to be applied to signal
            generator. Refer to programmer's guide for all available types.
            Defaults to 'FALLING'.
        trigger_source (str): The source that triggers the signal generator.
            Refer to programmer's guide for all available types.
            Defaults to 'SIGGEN_SOFT_TRIG'.
    """

    start_freq: float = 5.0E6
    end_freq: None = None
    increment: float = 0.0
    dwell: float = 1E-3
    offset_voltage: int = 0
    pk_to_pk: int = int(2E6)
    wave_type: int = WaveType.SQUARE.value
    sweep_type: int = SweepType.DOWN.value
    shots: int = 1
    sweeps: int = 0
    trigger_type: int = TriggerType.FALLING.value
    trigger_source: int = TriggerSource.SIGGEN_SOFT_TRIG.value
    samples_max: float = 1E4


@dataclass(frozen=True)
class TriggerProperties:
    """
    
    Attributes:
        threshold (int, optional): The ADC count at which the
            trigger will fire. Defaults to 300.
        direction (str, optional): The direction in which the
            signal must move to cause a trigger.
            Defaults to FALLING.
        delay (int, optional): The time, in sample periods,
            between the trigger occuring and the first sample
            being taken. Defaults to 0.
        autoTrigger_ms (int, optional): The number of milliseconds
            the device will wait if no trigger occurs.
            Defaults to 1000.
        enable_trigger (int, optional): Whether to enable trigger
            or not. Not used so don't mess with. Defaults to 1.
    """

    delay: PulsingParams.delay
    autoTrigger_ms: int = 1000
    direction: int = ThresholdDirection.FALLING.value
    enable_trigger: int = 1
    threshold: int = 5