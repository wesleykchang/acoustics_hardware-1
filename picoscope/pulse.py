"""Implementation of pulsing."""

import numpy as np
from typing import Callable, Dict, List

from picoscope.parameters import PulsingParams
from picoscope.picoscope import Picoscope2000
from picoscope.utils import parse_payload



class Pulse:
    """Implementation of oscilloscope pulsing.

    Follows procedure as laid out in Picoscope SDK manual, aside from
    opening the oscilloscope separately b/c there's a little bit of a time
    tax to it and we only need to run that particular function once, whereas
    we pulse a bunch of times.

    Not to be called externally, but rather through wrapper pulse.pulse()
    (not to be confused with method pulse.Pulse.pulse()).
    """

    def __init__(self, picoscope_: Picoscope2000):
        """
        Args:
            picoscope_ (Picoscope2000): Picoscope instance.
                picoscope_.connected() needs to be called
                prior to class initialization.
        Returns:
            np.ndarray: Results from pulse
        """

        self.picoscope_: Picoscope2000 = picoscope_
        self.preparation_fns: List[Callable] = [
            picoscope_.set_averaging,
            picoscope_.set_signal,
            picoscope_.set_channel,
            picoscope_.set_trigger,
            picoscope_.check_timebase
        ]
        self.pulsing_fns: List[Callable] =[
            picoscope_.make_buffer,
            picoscope_.register_buffer,
            picoscope_.run_block,
            picoscope_.pull_trigger,
            picoscope_.wait_ready,
            picoscope_.get_data,
            picoscope_.stop
        ]

    def prepare(self, pulsing_params: PulsingParams) -> None:
        """Sets up oscilloscope prior to pulsing.
        
        Args:
            picoscope_ (Picoscope2000): Picoscope instance.
            pulsing_params (PulsingParams): Parameters for pulsing.
        """

        self.picoscope_.n_samples = pulsing_params.duration
        self.picoscope_.enum_voltage_range = pulsing_params.voltage_range
        self.picoscope_.trigger_properties = pulsing_params.delay
        
        for fn in self.preparation_fns:
            fn()

    def _pulse(self) -> None:
        """Calls all pulsing functions in sequence
        
        Args:
            picoscope_ (Picoscope2000): Picoscope instance.
        """

        for fn in self.pulsing_fns:
            fn()

    def pulse(self) -> np.ndarray:
        """Class wrapper for pulsing.
        
        Returns:
            np.ndarray: The averaged waveform.
        """
        # should we here have an anlogue shift? I don't think it's necessary, but need to test

        waveforms_mV = np.zeros((self.picoscope_.avg_num, self.picoscope_.n_samples))

        for segment in range(self.picoscope_.avg_num):
            self.picoscope_.segment_index = segment
            self._pulse()
            waveforms_mV[segment, :] = self.picoscope_.to_mV()

        return waveforms_mV


def pulse(picoscope_: Picoscope2000, pulsing_params: PulsingParams) -> Dict[str, List[float]]:
    """Wrapper for acoustic pulsing.

    Args:
        picoscope_ (Picoscope2000): Picoscope instance.
        pulsing_params (PulsingParams): Parameters for pulsing.

    Returns:
        list[float]: Results from pulse.
    """

    if not picoscope_.is_connected:
        picoscope_.connect()

    pulse_ = Pulse(picoscope_=picoscope_)
    pulse_.prepare(pulsing_params=pulsing_params)
    waveforms_mV = pulse_.pulse()

    return parse_payload(field=waveforms_mV)
