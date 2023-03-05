import ctypes

PORT: int = 5001

AVG_NUM: int = 1
SAMPLING_INTERVAL: float = 4E-9  # The selected sampling interval [s]
MAX_SAMPLING_RATE: float = 1E9  # The fastest possible sampling rate [1GS/s]

C_OVERSAMPLE = ctypes.c_int16(0)  # Oversampling factor
C_HANDLE = ctypes.c_int16()
C_OVERFLOW = ctypes.c_int16()
C_SERIAL: None = None

US_TO_S: float = 1e-6
COUPLING = IS_ENABLED = True
EXT_IN_THRESHOLD = START_INDEX = DOWNSAMPLING_RATIO \
    = DOWNSAMPLING_MODE = PRE_TRIGGER_SAMPLES = TIME_INDISPOSED_MS \
    = LP_READY = P_PARAMETER = ANALOG_OFFSET = 0