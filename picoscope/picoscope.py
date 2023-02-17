"""Bindings for C-level functions for interfacing with picoscope."""

import ctypes
import json
from typing import Callable

from picosdk.errors import PicoSDKCtypesError
from picosdk.functions import adc2mV, assert_pico_ok
from picosdk.ps4000 import ps4000
from picosdk.ps2000a import ps2000a

from picoscope.constants import (
    FN_NAMES,
    SweepType,
    ThresholdDirection,
    TriggerType,
    TriggerSource,
    WaveType
)

C_OVERSAMPLE = ctypes.c_int16(1)  # Oversampling factor
C_HANDLE = ctypes.c_int16()
C_OVERFLOW = ctypes.c_int16()
SEGMENT_INDEX: int = 0  # specifies memory segment
EXT_IN_THRESHOLD: int = 0
OPERATION_TYPE: int = 0  # Disable white noise


class Picoscope:
    """Picoscope base class.
    
    All class attributes are references to C-functions for calling
    instruments, hence the CamelCase.

    The baseclass should never be called directly, but rather from
    an instrument-class-specific subclass.
    """

    def __init__(self, fns: dict):
        self.OpenUnit = fns['OpenUnit']
        self.SetSigGenBuiltIn = fns['SetSigGenBuiltIn']
        self.SetChannel = fns['SetChannel']
        self.GetTimebase = fns['GetTimebase']
        self.SetSimpleTrigger = fns['SetSimpleTrigger']
        self.RunBlock = fns['RunBlock']
        self.SigGenSoftwareControl = fns['SigGenSoftwareControl']
        self.IsReady = fns['IsReady']
        self.SetDataBuffer = fns['SetDataBuffer']
        self.GetValues = fns['GetValues']
        self.Stop = fns['Stop']
        self.CloseUnit = fns['CloseUnit']

    def make_buffer(self, no_samples: int) -> None:
        """Generates a buffer to which data is dumped.

        Args:
            no_samples (int): Maximum number of samples to be collected.

        Returns:
            c_buffer (): Buffer to which oscilloscope data is dumped.
        """

        c_buffer = (ctypes.c_int16 * int(no_samples))()

        return c_buffer

    def connect(self) -> None:
        """Connects to oscilloscope.

        NOTE:
            Looping because the connection process
            mistifyingly always fails on the first try.
        """

        for _ in range(3):
            try:
                status = self.OpenUnit(ctypes.byref(C_HANDLE))
                assert_pico_ok(status)
                return
            except PicoSDKCtypesError:
                continue

        raise Exception('Picoscope connection unsuccessful.')

    def define_procedure(self,
                         type_: str,
                         **nondefault_params) -> None:
        """Sets up the signal generator to produce a waveType signal.

        If startFrequency != stopFrequency it will sweep.

        Note:
            All params are optional. Defaults defined in settings.json.
        
        Args:
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

        NOTE:
            If a trigger source other than 0 (SIGGEN_NONE) is specified,
            then either shots or sweeps, but not both, must be set to a
            non-zero value.

        Raises:
            ValueError: If end_freq > 2E4 [Hz].

        Example:
            picoscope.define_procedure(**params) <- Note the kwargs (double-star).
        """

        with open("picoscope/settings.json") as f:
            settings = json.load(f)

        sig_params = settings[type_]

        # Use nondefault params
        for parameter, value in nondefault_params.items():
            sig_params[parameter] = value

        # Why not use built-in enum in pico-sdk library?
        # Well, first of all it doesn't for wavetype and triggertype,
        # and secondly it requires the ps6000a driver, which increases
        # unnecessary overhead.
        wave_type = WaveType[sig_params['wave_type']].value
        sweep_type = SweepType[sig_params['sweep_type']].value
        trigger_type = TriggerType[sig_params['trigger_type']].value
        trigger_source = TriggerSource[sig_params['trigger_source']].value

        status = self.SetSigGenBuiltIn(C_HANDLE, sig_params['offset_voltage'],
                                       int(sig_params['pk_to_pk']), wave_type,
                                       sig_params['start_freq'],
                                       sig_params['end_freq'],
                                       sig_params['increment'],
                                       sig_params['dwell'], sweep_type,
                                       OPERATION_TYPE, sig_params['shots'],
                                       sig_params['sweeps'], trigger_type,
                                       trigger_source, EXT_IN_THRESHOLD)

        assert_pico_ok(status)

    def set_channel_params(self,
                           enum_voltage_range: int,
                           channel: int,
                           is_channel: bool = True,
                           is_dc: bool = True) -> None:
        """Sets various channel parameters.

        Args:
            enum_voltage_range (int): Enum specifying measuring voltage range.
                Refer to programmer's manual for further info.
            channel (int): Picoscope channel, either 0 (A) or 1 (B).
            is_channel (bool, optional): Whether to enable channel or not.
                Not to be tinkered with. Defaults to True.
            is_dc (bool, optional): Specifies AC/DC coupling mode.
                Not to be tinkered with. Defaults to True.
        """

        status = self.SetChannel(C_HANDLE, channel, is_channel, is_dc,
                                 enum_voltage_range)

        assert_pico_ok(status)

    def get_timebase(self, enum_sampling_interval: int,
                     no_samples: int) -> None:
        """Basically sets the sampling rate.

        There's a whole section devoted to this subject in the
        programmer's guide.

        Args:
            enum_sampling_rate (int): Enumerated sampling rate.
                See utils.calculate_sampling_rate().
            no_samples (int): Number of samples to be collected.

        """

        time_interval_ns = ctypes.c_int32()
        c_max_samples = ctypes.c_int32(no_samples)
        n_samples = no_samples

        status = self.GetTimebase(C_HANDLE, enum_sampling_interval, n_samples,
                                  ctypes.byref(time_interval_ns), C_OVERSAMPLE,
                                  ctypes.byref(c_max_samples), SEGMENT_INDEX)

        assert_pico_ok(status)

    def set_simple_trigger(self,
                           channel: int,
                           threshold: int = 5,
                           direction: int = "FALLING",
                           delay: int = 0,
                           autoTrigger_ms: int = 1000,
                           enable_trigger: int = 1) -> None:
        """Cocks the gun.

        Args:
            channel (int): Picoscope channel, either 0 (A) or 1 (B).
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

        threshold_direction = ThresholdDirection[direction].value

        status = self.SetSimpleTrigger(C_HANDLE, enable_trigger, channel,
                                       threshold, threshold_direction, delay,
                                       autoTrigger_ms)

        assert_pico_ok(status)

    def run_block(self, enum_sampling_interval: int, no_samples: int) -> None:
        """Starts collecting data.
        
        Args:
            enum_sampling_rate (int): Enumerated sampling rate.
                See utils.calculate_sampling_rate().
            no_samples (int): Number of samples to be collected.
        """

        pre_trigger_samples = 0
        post_trigger_samples = no_samples
        time_indisposed_ms = 0
        lp_ready = 0
        p_parameter = 0

        status = self.RunBlock(C_HANDLE, pre_trigger_samples,
                               post_trigger_samples, enum_sampling_interval,
                               C_OVERSAMPLE, time_indisposed_ms, SEGMENT_INDEX,
                               lp_ready, p_parameter)

        assert_pico_ok(status)

    def pull_trigger(self) -> None:
        """Pulls the trigger: Starts the sweep.
        
        Triggers the wave generator.
        """

        status = self.SigGenSoftwareControl(C_HANDLE, 0)

        assert_pico_ok(status)

    def wait_ready(self) -> None:
        """Waits for data collection to finish before data is collected."""

        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)

        while ready.value == check.value:
            status = self.IsReady(C_HANDLE, ctypes.byref(ready))

            assert_pico_ok(status)

    def set_data_buffer(self, channel: int, no_samples: int, c_buffer) -> None:
        """Allocates memory to receive the oscilloscope to dump from memory.

        C-type stuff.

        Args:
            channel (int): Picoscope channel, either 0 (A) or 1 (B).
            no_samples (int): Number of samples to be collected.
            c_buffer (): Buffer to which data is dumped.
        """

        buffer_length = no_samples

        # Note that we use the pseudo-pointer byref
        status = self.SetDataBuffer(C_HANDLE, channel, ctypes.byref(c_buffer),
                                    buffer_length)

        assert_pico_ok(status)

    def get_data(self, no_samples: int) -> None:
        """Pulls the data from the oscilloscope.
        
        Args:
            no_samples (int): Number of samples to be collected.
        """

        start_index = 0
        downsample_ratio = 0
        downsample_ratio_mode = 0  # None
        c_max_samples = ctypes.c_int32(no_samples)

        status = self.GetValues(C_HANDLE, start_index,
                                ctypes.byref(c_max_samples), downsample_ratio,
                                downsample_ratio_mode, SEGMENT_INDEX,
                                ctypes.byref(C_OVERFLOW))

        assert_pico_ok(status)

    def stop(self) -> None:
        """Stops the picoscope, a necessary step at the end of each sweep.
        """

        status = self.Stop(C_HANDLE)

        assert_pico_ok(status)

        # Kills the signal generator
        status = self.SetSigGenBuiltIn(C_HANDLE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                       0, 1, 0, 0)

        assert_pico_ok(status)

    def disconnect(self) -> None:
        """Closes the oscilloscope connection, the opposite of connect().

        Generally speaking, this should only be used for tests.
        """

        status = self.CloseUnit(C_HANDLE)

        assert_pico_ok(status)

    def to_mV(self, enum_voltage_range: int, no_samples: int,
              c_buffer) -> list:
        """Converts amplitude in ADCs to mV.

        Args:
            enum_voltage_range (int): Enumerated voltage range.
            no_samples (int): Number of samples to be collected.
            c_buffer (): Buffer to which data is dumped.

        Returns:
            list[float]: Amplitudes in mV.
        """

        c_max_ADC = ctypes.c_int16(no_samples)

        return adc2mV(c_buffer, enum_voltage_range, c_max_ADC)


class Picoscope4000(Picoscope):
    """Subclass for 4000-level picoscopes. We have a 4262 model."""

    def __init__(self):
        c_functions = [
            ps4000.ps4000OpenUnit, ps4000.ps4000SetSigGenBuiltIn,
            ps4000.ps4000SetChannel, ps4000.ps4000GetTimebase,
            ps4000.ps4000SetSimpleTrigger, ps4000.ps4000RunBlock,
            ps4000.ps4000SigGenSoftwareControl, ps4000.ps4000IsReady,
            ps4000.ps4000SetDataBuffer, ps4000.ps4000GetValues,
            ps4000.ps4000Stop, ps4000.ps4000CloseUnit
        ]
        functions = dict(zip(FN_NAMES, c_functions))

        super(Picoscope4000, self).__init__(fns=functions)


class Picoscope2000(Picoscope):
    """Subclass for 2000A-level picoscopes.
    We have the 2208b and 2207b models.
    """

    def __init__(self):
        c_functions = [
            ps2000a.ps2000aOpenUnit, ps2000a.ps2000aSetSigGenBuiltIn,
            ps2000a.ps2000aSetChannel, ps2000a.ps2000aGetTimebase,
            ps2000a.ps2000aSetSimpleTrigger, ps2000a.ps2000aRunBlock,
            ps2000a.ps2000aSigGenSoftwareControl, ps2000a.ps2000aIsReady,
            ps2000a.ps2000aSetDataBuffer, ps2000a.ps2000aGetValues,
            ps2000a.ps2000aStop, ps2000a.ps2000aCloseUnit
        ]
        functions = dict(zip(FN_NAMES, c_functions))

        super(Picoscope2000, self).__init__(fns=functions)
