from dataclasses import dataclass, is_dataclass, fields
from collections.abc import Mapping, Set
from functools import partial
from typing import Union, List, Tuple

import numpy as np
import torch

try:
    import cupy as cp
except ImportError:
    cp = np

is_array = lambda x: isinstance(x, np.ndarray) or isinstance(x, cp.ndarray) or isinstance(x, torch.Tensor)
is_numeric = lambda x: isinstance(x, int) or isinstance(x, float) or isinstance(x, complex)

def recursive_map(data, func):
    """Recursively performs func on the items of data
    Only recurses through data that is not numerical arrays"""
    apply = lambda x: recursive_map(x, func)
    if isinstance(data, Mapping):
        return type(data)({k: apply(v) for k, v in data.items()})
    elif (isinstance(data, list) or isinstance(data, tuple)) and not is_array(data):
        return type(data)(apply(v) for v in data)
    elif is_dataclass(data):
        return type(data)(**{field: apply(getattr(data, field)) for field in fields(data)})
    else:
        return func(data)

def is_builtin(obj):
    return obj.__class__.__module__ == 'builtins'

def to_nested_mapping(data):
    apply = lambda x: to_nested_mapping(x)
    if is_numeric(data) or isinstance(data, str) or is_array(data):
        return data
    elif isinstance(data, Mapping):
        return type(data)({k: apply(v) for k, v in data.items()})
    elif isinstance(data, list) or isinstance(data, tuple):
        return type(data)(apply(v) for v in data)
    return apply(data.__dict__)


def recursive_map_pair(data1, data2, func):
    """Recursively performs func on the items of data1 and data2
    Assumes data1 and data2 have same substructure
    Only recurses through data1 that is not numerical arrays"""
    apply = lambda x1, x2: recursive_map_pair(x1, x2, func)
    if isinstance(data1, Mapping):
        return type(data1)({k: apply(data1[k], data2[k]) for k in data1.keys()})
    elif isinstance(data1, Union[list, tuple]) and not isinstance(data, ARRAYTYPE):
        return type(data1)(apply(v1, v2) for v1, v2 in zip(data1, data2))
    else:
        return func(data1, data2)

#####################
# [Cuda] -> [Numpy] #
#####################

def tonp(arr):
    """Converts an input array to a cpu np array if it is
    either a torch tensor or a cupy array"""
    if isinstance(arr, torch.Tensor):
        return arr.cpu().numpy()
    elif (cp != np) and isinstance(arr, cp.ndarray):
        return arr.get()
    return arr


def jsonify(data):
    """First converts array to numpy, then converts to a list
    method to make it jsonifiable
    """
    if is_array(data):
        return tonp(data).view('int64').tolist()
    return data

#####################
# [Numpy] -> [Cuda] #
#####################

CPU = 'cpu'
def devicestr(arr):
    if isinstance(arr, cp.ndarray):
        if hasattr(arr, 'device'): # cupy array
            if arr.device.id >= 0:
                return f'{arr.device.id}'
        return CPU
    elif isinstance(arr, np.ndarray):
        return CPU
    elif isinstance(arr, torch.Tensor):
        if arr.device.index:
            return f'cuda:{arr.device.index}'
    return type(arr).__name__


def totorch(arr: np.ndarray, device):
    return torch.from_numpy(arr).to(device)


def tocupy(arr: np.ndarray):
    return cp.array(arr)


class Np2Torch:
    def __init__(self, device_idx: int = -1):
        """
        device_idx = -1 (cpu) or 0+ (gpu)
        """

        self.device_idx = device_idx

    def __call__(self, data):
        use_cuda = torch.cuda.is_available() and self.device_idx >= 0
        device = torch.device(
            f'cuda:{self.device_idx}' if use_cuda else 'cpu'
        )
        return recursive_map_np(
            data,
            partial(totorch, device=device)
        )

class Np2Cupy:
    def __init__(self, device_idx=-1):
        self.device_idx = device_idx

    def __call__(self, data):
        with cp.device.Device(self.device_idx):
            return recursive_map_np(data, tocupy)
