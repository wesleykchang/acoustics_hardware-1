""""Picoscope parameters."""

from dataclasses import dataclass
import numpy as np
from enum import Enum, auto

from picoscope import constants


def builtin_voltage_ranges() -> np.ndarray:
    """Used to map input voltage range to enumerated voltage range.

    Returns:
        np.ndarray: Built-in voltage ranges.
    """
    return np.asarray([2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1., 2., 5., 10., 20.])


def available_sampling_intervals() -> np.ndarray:
    """For mapping raw sampling intervals (seconds) to enumerated sampling intervals.

    Returns:
        np.ndarray: Built-in sampling intervals.
    """
    return 2**np.arange(0, 1000) / constants.MAX_SAMPLING_RATE


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

    All other parameters are lower-level and thus not be tinkered
    with on the fly, but rather by ssh-ing into the container.

    Args:
        delay (int): How long to wait between trigger being pulled
            and starting collecting data [us].
        voltage_range (int): A proxy for gain of receiving transducer [V].
        duration (int): Duration of which data is collected [us].
    """

    delay: int
    voltage_range: int
    duration: int


@dataclass
class TriggerProperties:
    """Sets parameters for how trigger should be pulled.
    
    Attributes:
        delay (int): The time, in sample periods,
            between the trigger occuring and the first sample
            being taken. Therefore note that it is different
            from PulsingParams.delay, which is why we parse it
            here.
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
    direction: int = ThresholdDirection.RISING.value
    enable_trigger: int = 1
    threshold: int = 10
    channel: int = Channel.A.value

    def set_delay(self, delay_us: int) -> None:
        """Sets the delay.
        
        Note that it is defined in number of samples from trigger being pulled,
        not seconds.
        
        Args:
            delay_us (int): Delay in microseconds.
            sampling_interval (float): The timebase, i.e. the time
                that passes between samples being collected.
        """
        delay = delay_us * constants.US_TO_S / constants.SAMPLING_INTERVAL
        self.delay = int(round(delay, -2))
