from dataclasses import dataclass, field
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


class WaveType(Enum):
    SINE = 0
    SQUARE = 1
    DC_VOLTAGE = 3

@dataclass
class PulsingParams:
    """All the params that should should be passed
    to a pulsing picoscope, no more, no less.

    Args:
        delay (int): Delay in microseconds.

    """

    delay: int
    voltage: int
    duration: int
    avg_num: int


@dataclass(frozen=True)
class SignalProperties:
    """Properties passed to setup_signal()

    Attributes:
        offset_voltage (int, optional): The voltage offset [uV].
            Defaults to 0.
        pk_to_pk (int, optional): Peak-to-peak voltage [uV].
            Defaults to 2E6.
        wave_type (int, optional): The type of waveform to be generated.
            Refer to programmer's guide for all available types.
            Defaults to 0 (Sine).
        start_freq (float, optional): Starting frequency.
            Defaults to 1.0E6.
        end_freq (float, optional): Stopping (or reversing) frequency (included).
            Defaults to 1.0E6.
        increment (float, optional): The amount by which the frequency rises (or falls).
            Defaults to 0.0.
        dwell_time (float, optional): The time [s] between frequency changes.
            Defaults to 1E-3.
        dwell_time (int): Determines sweeping type.
            Refer to programmer's guide for all available types.
            Defaults to 1 (UP).
        shots (int, optional): The number of cycles of the waveform to be produced
            after a trigger event. Defaults to 1.
        sweeps (int, optional): Number of sweep repetitions. Defaults to 0.
            If a trigger source other than 0 (SIGGEN_NONE) is specified,
            then either shots or sweeps, but not both, must be set to a
            non-zero value.
        trigger_type (int, optional): The type of trigger to be applied to signal
            generator. Refer to programmer's guide for all available types.
            Defaults to  0 (FALLING).
        trigger_source (int, optional): The source that triggers the signal generator.
            Refer to programmer's guide for all available types.
            Defaults to 0 (SIGGEN_SOFT_TRIG).
    """

    offset_voltage: int = 0
    pk_to_pk: int = 2
    wave_type: int = WaveType.SINE.value
    start_freq: float = 1.0E6
    end_freq: float = 1.0E6
    increment: float = 0.0
    dwell: float = 1E-3
    sweep_type: int = SweepType.UP.value
    operation: int = 0
    shots: int = 1
    sweeps: int = 0
    trigger_type: int = TriggerType.FALLING.value
    trigger_source: int = TriggerSource.SIGGEN_SOFT_TRIG.value
    ext_in_threshold: int = 0


@dataclass
class TriggerProperties:
    """
    
    Attributes:
        delay (int): The time, in sample periods,
            between the trigger occuring and the first sample
            being taken. Therefore note that it is different
            from PulsingParams.delay, which is why we parse it
            here
        threshold (int, optional): The ADC count at which the
            trigger will fire. Defaults to 5.
        direction (str, optional): The direction in which the
            signal must move to cause a trigger.
            Defaults to FALLING.
        autoTrigger_ms (int, optional): The number of milliseconds
            the device will wait if no trigger occurs.
            Defaults to 1000.
        enable_trigger (int, optional): Whether to enable trigger
            or not. Not used so don't mess with. Defaults to 1.
    """
 
    delay: int = None
    autoTrigger_ms: int = 1000
    direction: int = ThresholdDirection.FALLING.value
    enable_trigger: int = 1
    threshold: int = 5

    def set_delay(self, delay_us: int, sampling_interval: float):
        self.delay = int(delay_us * 1e-6 / sampling_interval)