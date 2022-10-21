from enum import Enum, auto

FN_NAMES = [
    'OpenUnit', 'SetSigGenBuiltIn', 'SetChannel', 'GetTimebase',
    'SetSimpleTrigger', 'RunBlock', 'SigGenSoftwareControl', 'IsReady',
    'SetDataBuffer', 'GetValues', 'Stop', 'CloseUnit'
]



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