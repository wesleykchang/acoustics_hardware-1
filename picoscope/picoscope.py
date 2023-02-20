"""Bindings for C-level functions for interfacing with picoscope."""

import ctypes
from typing import Dict, Callable

from picosdk.errors import PicoSDKCtypesError
from picosdk.functions import adc2mV, assert_pico_ok
from picosdk.ps2000a import ps2000a

from picoscope.constants import Channel, SignalProperties, TriggerProperties

C_OVERSAMPLE = ctypes.c_int16(0)  # Oversampling factor
C_HANDLE = ctypes.c_int16()
C_OVERFLOW = ctypes.c_int16()

# TODO: Tidy up
COUPLING = IS_ENABLED = True
EXT_IN_THRESHOLD = START_INDEX = DOWNSAMPLING_RATIO = DOWNSAMPLING_MODE = \
     OPERATION_TYPE = SEGMENT_INDEX = PRE_TRIGGER_SAMPLES = TIME_INDISPOSED_MS = LP_READY = P_PARAMETER = 0
C_SERIAL: None = None

SAMPLING_INTERVAL: int = int(2E-9)
signal_properties: SignalProperties = SignalProperties()


class Picoscope:
    """Picoscope base class.
    
    All class attributes are references to C-functions for calling
    instruments, hence the CamelCase.

    The baseclass should never be called directly, but rather from
    an instrument-class-specific subclass.
    """

    def __init__(self, fns: Dict[str, Callable], channel: Channel = Channel.B) -> None:
        self.OpenUnit = fns['OpenUnit']
        self.SetSigGenBuiltIn = fns['SetSigGenBuiltIn']
        self.SetChannel = fns['SetChannel']
        self.GetTimebase2 = fns['GetTimebase2']
        self.SetSimpleTrigger = fns['SetSimpleTrigger']
        self.RunBlock = fns['RunBlock']
        self.SigGenSoftwareControl = fns['SigGenSoftwareControl']
        self.IsReady = fns['IsReady']
        self.SetDataBuffer = fns['SetDataBuffer']
        self.GetValues = fns['GetValues']
        self.Stop = fns['Stop']
        self.CloseUnit = fns['CloseUnit']
        self.GetAnalogueOffset = fns['GetAnalogueOffset']

        self._channel = channel.value
        # self.n_samples = None  # this may be have to defined as None and then defined in a separate method to account for timebasing

    def set_n_samples(self, duration: int) -> None:
        """
        
        Args:
            duration (int): In microseconds.
        """
        self.n_samples = int(duration * 1e-6 / SAMPLING_INTERVAL)

    def make_buffer(self) -> ctypes.Array:
        """Generates a buffer to which data is dumped.

        Returns:
            ctypes.Array[ctypes.c_int16]: Buffer to which oscilloscope data is dumped.
        """

        return (ctypes.c_int16 * int(self.n_samples))()

    def connect(self) -> None:
        """Connects to oscilloscope.

        NOTE:
            Looping because the connection process
            mistifyingly always fails on the first try.
        """

        for _ in range(3):
            try:
                status = self.OpenUnit(ctypes.byref(C_HANDLE), C_SERIAL)
                assert_pico_ok(status)

                return
            
            except PicoSDKCtypesError:
                continue

        raise Exception('Picoscope connection unsuccessful.')

    def define_procedure(self) -> None:
        """Sets up the signal generator to produce a waveType signal.
        NOTE:
            If a trigger source other than 0 (SIGGEN_NONE) is specified,
            then either shots or sweeps, but not both, must be set to a
            non-zero value.

        Example:
            picoscope.define_procedure(**params) <- Note the kwargs (double-star).
        """

        status = self.SetSigGenBuiltIn(
            C_HANDLE,
            signal_properties.offset_voltage,
            signal_properties.pk_to_pk,
            signal_properties.wave_type,
            signal_properties.start_freq,
            signal_properties.end_freq,
            signal_properties.increment,
            signal_properties.dwell,
            signal_properties.sweep_type,
            OPERATION_TYPE,
            signal_properties.shots,
            signal_properties.sweeps,
            signal_properties.trigger_type,
            signal_properties.trigger_source,
            EXT_IN_THRESHOLD
        )

        assert_pico_ok(status)

    def get_analogue_offset(self, voltage: int) -> float:
        """
        
        Args:
            voltage (int): Enumerated voltage. See settings.json.

        Returns:
            float: Max analogue offset [V]. Only max_voltage is returned
                as max_voltage = -min_voltage.
        """
        
        min_voltage = ctypes.c_float()
        max_voltage = ctypes.c_float()

        status = self.GetAnalogueOffset(
            C_HANDLE,
            voltage,
            COUPLING,
            ctypes.byref(max_voltage),
            ctypes.byref(min_voltage)
        )

        assert_pico_ok(status)

        return max_voltage.value

    def set_channel(self, enum_voltage_range: int) -> None:
        """Sets various channel parameters.

        Args:
            voltage (Voltage): Enumerated voltage.
        """

        analog_offset = 0

        status = self.SetChannel(
            C_HANDLE,
            self._channel,
            IS_ENABLED,
            COUPLING,
            enum_voltage_range,
            analog_offset
        )

        assert_pico_ok(status)

    def check_timebase(self) -> None:
        """Checks whether set sampling interval is valid.

        There's a whole section devoted to this subject in the
        programmer's guide.

        Args:
            enum_sampling_rate (int): Enumerated sampling rate.
                See utils.calculate_sampling_rate().
            n_samples (int): Number of samples to be collected.

        """

        enum_sampling_interval = 1  # Always running at top speed

        time_interval_ns = ctypes.c_float()
        returned_max_samples = ctypes.c_int32()

        status = self.GetTimebase2(
            C_HANDLE,
            enum_sampling_interval,
            self.n_samples,
            ctypes.byref(time_interval_ns),
            C_OVERSAMPLE,
            ctypes.byref(returned_max_samples),
            SEGMENT_INDEX
        )

        assert_pico_ok(status)

    def set_simple_trigger(self, trigger_properties: TriggerProperties) -> None:
        """Cocks the gun."""

        status = self.SetSimpleTrigger(
            C_HANDLE,
            trigger_properties.enable_trigger,
            self._channel,
            trigger_properties.threshold,
            trigger_properties.direction,
            trigger_properties.delay,
            trigger_properties.autoTrigger_ms
        )

        assert_pico_ok(status)

    def run_block(self, enum_sampling_interval: int) -> None:
        """Starts collecting data.
        
        Args:
            enum_sampling_rate (int): Enumerated sampling rate.
                See utils.calculate_sampling_rate().
            no_samples (int): Number of samples to be collected.
        """

        post_trigger_samples = self.n_samples

        status = self.RunBlock(
            C_HANDLE,
            PRE_TRIGGER_SAMPLES,
            post_trigger_samples,
            enum_sampling_interval,
            C_OVERSAMPLE,
            TIME_INDISPOSED_MS,
            SEGMENT_INDEX,
            LP_READY,
            P_PARAMETER
        )

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

    def set_data_buffer(self, c_buffer: ctypes.Array) -> None:
        """Allocates memory to receive the oscilloscope to dump from memory.

        C-type stuff.

        Args:
            c_buffer (): Buffer to which data is dumped.
        """

        buffer_length: int = self.n_samples

        status = self.SetDataBuffer(
            C_HANDLE,
            self._channel,
            ctypes.byref(c_buffer),
            buffer_length,
            SEGMENT_INDEX,
            DOWNSAMPLING_MODE
        )

        assert_pico_ok(status)

    def get_data(self) -> None:
        """Pulls the data from the oscilloscope.
        
        Args:
            no_samples (int): Number of samples to be collected.
        """

        c_max_samples = ctypes.c_int32(self.n_samples)

        status = self.GetValues(
            C_HANDLE,
            START_INDEX,
            ctypes.byref(c_max_samples), 
            DOWNSAMPLING_RATIO,
            DOWNSAMPLING_MODE,
            SEGMENT_INDEX,
            ctypes.byref(C_OVERFLOW)
        )

        assert_pico_ok(status)

    def stop(self) -> None:
        """Wrapper for stopping the picoscope, a necessary step at the end of each pulse.
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

    def to_mV(self, enum_voltage_range: int, c_buffer: ctypes.Array) -> list:
        """Converts amplitude in ADCs to mV.

        Args:
            enum_voltage_range (int): Enumerated voltage range.
            no_samples (int): Number of samples to be collected.
            c_buffer (): Buffer to which data is dumped.

        Returns:
            list[float]: Amplitudes in mV.
        """

        c_max_ADC = ctypes.c_int16(self.n_samples)

        return adc2mV(c_buffer, enum_voltage_range, c_max_ADC)


class Picoscope2000(Picoscope):
    """Subclass for 2000A-level picoscopes.
    We have the 2208b and 2207b models.

    Confusingly, they are 2000A-level, despite being appended by a 'b'.
    """

    def __init__(self):
        functions: Dict[str, Callable] = {
            'OpenUnit': ps2000a.ps2000aOpenUnit,
            'SetSigGenBuiltIn': ps2000a.ps2000aSetSigGenBuiltIn,
            'SetChannel': ps2000a.ps2000aSetChannel,
            'GetTimebase2': ps2000a.ps2000aGetTimebase2,
            'SetSimpleTrigger': ps2000a.ps2000aSetSimpleTrigger,
            'RunBlock': ps2000a.ps2000aRunBlock,
            'SigGenSoftwareControl': ps2000a.ps2000aSigGenSoftwareControl,
            'IsReady': ps2000a.ps2000aIsReady,
            'SetDataBuffer': ps2000a.ps2000aSetDataBuffer,
            'GetValues': ps2000a.ps2000aGetValues,
            'Stop': ps2000a.ps2000aStop,
            'CloseUnit': ps2000a.ps2000aCloseUnit,
            'GetAnalogueOffset': ps2000a.ps2000aGetAnalogueOffset,
        }

        super(Picoscope2000, self).__init__(fns=functions)
