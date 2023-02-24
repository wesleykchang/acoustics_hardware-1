"""Bindings for C driver functions for interfacing with picoscope."""

import ctypes
from typing import Callable, Dict, List

from picosdk.errors import PicoSDKCtypesError
from picosdk.functions import adc2mV, assert_pico_ok
from picosdk.ps2000a import ps2000a

from picoscope import parameters, utils

C_OVERSAMPLE = ctypes.c_int16(0)  # Oversampling factor
C_HANDLE = ctypes.c_int16()
C_OVERFLOW = ctypes.c_int16()

# TODO: Tidy up
COUPLING = IS_ENABLED = True
EXT_IN_THRESHOLD = START_INDEX = DOWNSAMPLING_RATIO = DOWNSAMPLING_MODE \
     =  PRE_TRIGGER_SAMPLES = TIME_INDISPOSED_MS = LP_READY = P_PARAMETER = 0
C_SERIAL: None = None

# TODO: Move elsewhere
ANALOG_OFFSET = 0


class Picoscope:
    """Picoscope base class. Contains all functions for interfacing with picoscope.
    
    All class attributes are references to C-functions for calling
    instruments, hence the CamelCase.

    The baseclass is not called directly, but from an instrument-class-specific subclass.

    Attributes:
        signal_properties (SignalProperties): The signal configuration parameters.
            Are generally not modified between experiments.
        sampling_interval (float, optional): The desired sampling interval. Defaults
            to 2E-9 (equal to 500MS/s sampling rate). 
        channel (Channel, optional): The channel to which the receiving transducer
            is connected. Defaults to Channel.B. 
    """

    sampling_interval: float = 2E-9
    input_channel: int = parameters.Channel.B.value
    avg_num: int = 8
    enum_sampling_interval: int = utils.to_enum(
        val=sampling_interval,
        arr_fn=parameters.available_sampling_intervals
    )

    def __init__(self, fns: Dict[str, Callable]) -> None:
        """
        
        Args:
            fns (Dict[str, Callable]): Mapping of a readable name to SDK functions.
        """

        self.OpenUnit: Callable = fns['OpenUnit']
        self.SetChannel: Callable = fns['SetChannel']
        self.GetTimebase2: Callable = fns['GetTimebase2']
        self.SetSimpleTrigger: Callable = fns['SetSimpleTrigger']
        self.RunBlock: Callable = fns['RunBlock']
        self.SigGenSoftwareControl: Callable = fns['SigGenSoftwareControl']
        self.IsReady: Callable = fns['IsReady']
        self.SetDataBuffer: Callable = fns['SetDataBuffer']
        self.GetValues: Callable = fns['GetValues']
        self.Stop: Callable = fns['Stop']
        self.CloseUnit: Callable = fns['CloseUnit']
        self.GetAnalogueOffset: Callable = fns['GetAnalogueOffset']
        self.SetNoOfCaptures: Callable = fns['SetNoOfCaptures']
        self.MemorySegments: Callable = fns['MemorySegments']
        self.PingUnit: Callable = fns['PingUnit']

        self._n_samples: int = None
        self._is_connected: bool = False
        self._c_buffer: ctypes.Array = None
        self._enum_voltage_range: int = None
        self._segment_index: int = 0  # Not None bc it's called during pulse preparation.
        self._trigger_properties: parameters.TriggerProperties = parameters.TriggerProperties()

    @property
    def n_samples(self) -> int:
        """Number of samples per single pulse
        
        We need to access it externally when preallocating for data.
        
        Returns:
            int: Number of samples per single pulse.
        """
        return self._n_samples

    @n_samples.setter
    def n_samples(self, duration: int, unit_multiplier: float = 1e-6) -> None:
        """Sets number of samples to be collected per single pulse.

        Args:
            duration (int): The duration of the window where we collect data.
                The final unit should be in seconds, so if duration is in µs
                (which is usually the case) the unit_multiplier should be 1e-6.
            unit_multiplier (float, optional): Scales duration to seconds.
                Defaults to 1e-6.
        """

        _n_samples = duration * unit_multiplier / Picoscope.sampling_interval
        self._n_samples: int = int(round(_n_samples, -2))

    @property
    def enum_voltage_range(self):
        return self._enum_voltage_range

    @enum_voltage_range.setter
    def enum_voltage_range(self, voltage_range: float):
        self._enum_voltage_range = utils.to_enum(
            val=voltage_range,
            arr_fn=parameters.builtin_voltage_ranges
        )

    @property
    def trigger_properties(self):
        return self._trigger_properties

    @trigger_properties.setter
    def trigger_properties(self, delay: int):
        """Sets delay, the only nondefault trigger property.
        
        Args:
            delay (int): Microseconds
        """
        self._trigger_properties.set_delay(delay_us=delay)

    @property
    def segment_index(self):
        return self._segment_index
    
    @segment_index.setter
    def segment_index(self, segment: int):
        """Sets segment index, i.e. which memory segment the next pulse should be placed in.
        
        Used when averaging multiple waveforms. Not a a property because we never have to
        access it externally.

        Args:
            segment (int): The memory segment index.
        """
        self._segment_index = segment

    @property
    def is_connected(self):
        """Checks whether picoscope is connected.
        
        Convenience method to poll externally via http w/o
        having to ssh into the container.

        Returns:
            bool: True if connected, False if not.
        """

        status = self.PingUnit(C_HANDLE)

        try:
            assert_pico_ok(status)
            self._is_connected = True

        except PicoSDKCtypesError:
            self._is_connected = False

        return self._is_connected

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

        self.is_connected

        raise Exception('Picoscope connection unsuccessful.')

    def set_averaging(self) -> None:
        """Sets the number of waveforms to be collected for averaging.
        
        Args:
            avg_num (int): The number of waveforms to be collected.
        """

        status = self.SetNoOfCaptures(C_HANDLE, Picoscope.avg_num)

        assert_pico_ok(status)

        # Split memory to allow for storing multiple waveforms.
        n_max_samples = ctypes.c_int32(self._n_samples)
        status = self.MemorySegments(C_HANDLE, Picoscope.avg_num, ctypes.byref(n_max_samples))
        
        assert_pico_ok(status)

    def get_analogue_offset(self, voltage: int) -> float:
        """Gets analogue offset. Is this needed?
        
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

    def set_channel(self) -> None:
        """Sets various input channel parameters.

        Args:
            enum_voltage_range (Voltage): Enumerated voltage.
        """

        status = self.SetChannel(
            C_HANDLE,
            Picoscope.input_channel,
            IS_ENABLED,
            COUPLING,
            self.enum_voltage_range,
            ANALOG_OFFSET
        )

        assert_pico_ok(status)

    def check_timebase(self) -> None:
        """Checks whether set sampling interval is valid.

        There's a whole section devoted to this subject in the
        programmer's guide.
        """


        time_interval_ns = ctypes.c_float()
        returned_max_samples = ctypes.c_int32()

        status = self.GetTimebase2(
            C_HANDLE,
            Picoscope.enum_sampling_interval,
            self._n_samples,
            ctypes.byref(time_interval_ns),
            C_OVERSAMPLE,
            ctypes.byref(returned_max_samples),
            self.segment_index
        )

        assert_pico_ok(status)

    def set_trigger(self) -> None:
        """Cocks the gun.
        
        trigger_properties (TriggerProperties): See definition.
        """

        status = self.SetSimpleTrigger(
            C_HANDLE,
            self._trigger_properties.enable_trigger,
            self._trigger_properties.channel,
            self._trigger_properties.threshold,
            self._trigger_properties.direction,
            self._trigger_properties.delay,
            self._trigger_properties.autoTrigger_ms
        )

        assert_pico_ok(status)

    def run_block(self) -> None:
        """Specifies how data should be collected.
        
        Args:
            enum_sampling_rate (int): Enumerated sampling rate.
                See utils.calculate_sampling_rate().
            no_samples (int): Number of samples to be collected.
        """

        post_trigger_samples = self._n_samples

        status = self.RunBlock(
            C_HANDLE,
            PRE_TRIGGER_SAMPLES,
            post_trigger_samples,
            Picoscope.enum_sampling_interval,
            C_OVERSAMPLE,
            None,
            self.segment_index,
            None,
            None
        )

        assert_pico_ok(status)

    def pull_trigger(self) -> None:
        """Pulls the trigger: Sends a signal to the pulser."""

        status = self.SigGenSoftwareControl(C_HANDLE, 0)

        assert_pico_ok(status)

    def wait_ready(self) -> None:
        """A thread lock, waits for data collection to finish before data is collected."""

        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)

        while ready.value == check.value:
            status = self.IsReady(C_HANDLE, ctypes.byref(ready))

            assert_pico_ok(status)

    def set_buffer(self) -> None:
        """Create data buffer and register with driver."""

        self._c_buffer: ctypes.Array = (ctypes.c_int16 * self._n_samples)()
        buffer_length: int = self._n_samples

        status = self.SetDataBuffer(
            C_HANDLE,
            Picoscope.input_channel,
            ctypes.byref(self._c_buffer),
            buffer_length,
            self.segment_index,
            DOWNSAMPLING_MODE
        )

        assert_pico_ok(status)

    def get_data(self) -> None:
        """Pulls the data from the oscilloscope.
        
        Args:
            no_samples (int): Number of samples to be collected.
        """

        c_max_samples = ctypes.c_int32(self._n_samples)

        status = self.GetValues(
            C_HANDLE,
            START_INDEX,
            ctypes.byref(c_max_samples), 
            DOWNSAMPLING_RATIO,
            DOWNSAMPLING_MODE,
            self.segment_index,
            ctypes.byref(C_OVERFLOW)
        )

        assert_pico_ok(status)

    def stop(self) -> None:
        """Wrapper for stopping the picoscope, a necessary step at the end of each pulse.
        """

        status = self.Stop(C_HANDLE)

        assert_pico_ok(status)

    def to_mV(self) -> List[float]:
        """Converts amplitude in ADCs to mV.

        Args:
            enum_voltage_range (int): Enumerated voltage range.
            no_samples (int): Number of samples to be collected.
        
        Returns:
            list[float]: Amplitudes in mV.
        """

        c_max_ADC = ctypes.c_int16(self._n_samples)

        return adc2mV(self._c_buffer, self.enum_voltage_range, c_max_ADC)

    def disconnect(self) -> None:
        """Closes the oscilloscope connection, the opposite of connect().

        Generally speaking, this should only be used for tests.
        """

        status = self.CloseUnit(C_HANDLE)

        assert_pico_ok(status)


class Picoscope2000(Picoscope):
    """Subclass for 2000A-level picoscopes. We have the 2208b and 2207b models.

    Confusingly, they are 2000A-level, despite being appended by a 'b'.
    """

    def __init__(self):
        functions: Dict[str, Callable] = {
            'OpenUnit': ps2000a.ps2000aOpenUnit,
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
            'SetNoOfCaptures': ps2000a.ps2000aSetNoOfCaptures,
            'MemorySegments': ps2000a.ps2000aMemorySegments,
            'PingUnit': ps2000a.ps2000aPingUnit
        }

        super(Picoscope2000, self).__init__(fns=functions)
