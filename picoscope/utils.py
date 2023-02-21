"""Utility functions. Don't hate the player, hate the game.

All functions—aside from to_enum—have to do with parsing between
pythonic syntax and data sent/received through http.
"""

from dataclasses import fields
import numpy as np
from typing import Callable, Dict, List, Type, Union


def bool_to_requests(bool_: bool) -> str:
    """Parses a boolean to a format suitable for http, i.e. '0' or '1'.
    
    Args:
        bool_ (bool): A python boolean

    Returns:
        str: Either a '0' (False) or '1'.
    """
    
    assert isinstance(bool_, bool)

    return str(int(bool_))


def dataclass_from_dict(dataclass_: Type, dict_: dict) -> Type:
    """Populated dataclass from a dictionary.
    
    Used to parse incoming http dicts to a dataclass.

    Args:
        dataclass_ (Type): Dataclass object, i.e. not an instance of it.
        dict_ (dict): Dict that matches keys of dataclass_ **exactly**.

    Returns:
        Type: Dataclass instance, populated by values from dict.
    """

    field_set = {f.name for f in fields(dataclass_) if f.init}
    filtered_arg_dict = {k : v for k, v in dict_.items() if k in field_set}
    
    return dataclass_(**filtered_arg_dict)


def parse_dict_vals_to_int(dict_: Dict[str, Union[str, float]]) -> Dict[str, int]:
    """Parses dict_ values from str to int.

    Incoming dictionaries through http are always automatically read as
    of the format dict[str, str], even if the values should be of a
    numerical type.
    
    Args:
        dict_ (Dict[str, str]):

    Returns:
        Dict[str, int]
    """
    return dict([key, int(val)] for key, val in dict_.items())


def parse_payload(field: np.ndarray, key: str = 'amps') -> Dict[str, List[float]]:
    """Parses _field_ to a http-payload-ready format.
    
    Args:
        field (np.ndarray): A numerical array (here, usually waveform).
        key (str, optional): Field name.

    Returns:
        Dict[str, List[float]]: Http-ready data.
    """

    payload: Dict[str, List[float]] = dict()
    payload[key] = np.mean(field, axis=0).tolist()

    return payload


def to_enum(val: Union[int, float], arr_fn: Callable) -> int:
    """Parses val to enum based on arr_fn.

    Finds the index of the value in the array closest to the passed _val_.
    
    Args:
        val (Union[int, float]): Any numerical value.
        arr_fn (Callable): The function should, when called, return
            a sequence of numbers.
    """

    arr = arr_fn()
    index: np.int64 = (np.abs(arr - val)).argmin()

    return int(index)
