from dataclasses import fields
import numpy as np
from typing import Dict, Union, Callable

from picoscope.constants import PulsingParams


def dataclass_from_dict(dataclass_, dict_: dict):
    """Populated dataclass from a dictionary.
    
    Used to parse incoming http dicts to a dataclass.

    Args:
        dataclass_ (): Dataclass object, i.e. not an instance of it.
        dict_ (dict): Dict that matches keys ot dataclass_ exactly.
    """
    field_set = {f.name for f in fields(dataclass_) if f.init}
    filtered_arg_dict = {k : v for k, v in dict_.items() if k in field_set}
    
    return dataclass_(**filtered_arg_dict)


def parse_incoming_params(raw_params: Dict[str, str]) -> PulsingParams:
    """Parses incoming JSON to a Dataclass.
    
    The raw incoming JSON has str-str key-value pairs.
    This is the case even if the actual value is a float. We ameliorate
    that here and then convert to PulsingParams dataclass.

    Args:
        raw_params (RawParams): Raw incoming params,
            e.g. {'start_freq': '10.0'}.

    Returns:
        ParsedParams: Values ready to be passed to picoscope,
            e.g. {'start_freq': 10.0}
    """

    parsed_params = dict([key, int(val)] for key, val in raw_params.items())
    pulsing_params = dataclass_from_dict(
        dataclass_=PulsingParams,
        dict_=parsed_params
    )
        
    return pulsing_params


def parse_to_enum(val: Union[int, float], arr_fn: Callable) -> int:
    """Parses val to enum based on arr_fn.

    It finds the index of the value in the array closest to the passed _val_.
    
    Args:
        val (Union[int, float]): Any numerical value.
        arr_fn (Callable): The function should, when called, return
            a sequence of numbers.
    """

    arr = arr_fn()

    return (np.abs(arr - val)).argmin()
