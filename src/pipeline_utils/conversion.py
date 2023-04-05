from dataclasses import dataclass, is_dataclass, fields
from collections.abc import Mapping, Set
from functools import partial
from typing import Union, List, Tuple, Any, Optional

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
    Only recurses through data that is not numerical arrays
    Converts objects to dicts"""
    apply = lambda x: recursive_map(x, func)
    if is_numeric(data) or isinstance(data, str) or is_array(data):
        return func(data)
    elif isinstance(data, Mapping):
        return type(data)({k: apply(v) for k, v in data.items()})
    elif (isinstance(data, list) or isinstance(data, tuple)):
        return type(data)(apply(v) for v in data)
    return apply(data.__dict__)


def recursive_apply_inplace(data, func):
    """Recursive performs func on the items of data
    Does operation in-place, i.e. without copying data."""
    apply = lambda x: recursive_apply_inplace(x, func)
    if (is_numeric(data)
        or isinstance(data, str)
        or is_array(data)):
        return func(data)
    elif isinstance(data, Mapping):
        for k, v in data.items():
            data[k] = apply(v)
    elif isinstance(data, list):
        for i, v in enumerate(data):
          data[i] = apply(v)
    elif isinstance(data, tuple):
        raise ValueError('Cannot modify tuple inplace.')
    else:
        apply(data.__dict__)


def to_nested_mapping(data):
    apply = lambda x: to_nested_mapping(x)
    if (is_numeric(data)
        or isinstance(data, str)
        or is_array(data)):
        return data
    elif isinstance(data, Mapping):
        return type(data)({k: apply(v) for k, v in data.items()})
    elif isinstance(data, list) or isinstance(data, tuple):
        return type(data)(apply(v) for v in data)
    return apply(data.__dict__)


def recursive_map_pair(data1, data2, func):
    """Recursively performs func on the items of data1 and data2
    Assumes data1 and data2 have same substructure
    Only recurses through data1 that is not numerical arrays, numerics, or strings"""
    apply = lambda x1, x2: recursive_map_pair(x1, x2, func)
    if is_numeric(data1) or isinstance(data1, str) or is_array(data1):
        return func(data1, data2)
    elif isinstance(data1, Mapping):
        return type(data)({k: apply(v) for k, v in data.items()})
    elif (isinstance(data, list) or isinstance(data, tuple)):
        return type(data)(apply(v) for v in data)
    return apply(data.__dict__)


@dataclass
class DeviceArray:
    arr: np.ndarray
    device: Any
    mode: str

    @classmethod
    def infer(cls, data):
        if isinstance(data, torch.Tensor):
            return cls(data.cpu().numpy(), data.device, 'torch')
        elif (cp != np) and isinstance(data, cp.ndarray):
            return cls(data.get(), data.Device, 'cupy')
        elif isinstance(data, np.ndarray):
            return cls(data, None, 'numpy')
        return data


    @classmethod
    def unpack(cls, data, device_idx=None):
        if isinstance(data, DeviceArray):
            if data.mode == 'torch':
                if device_idx is None:
                    device = data.device
                else:
                    device = torch.device(
                        f'cuda:{device_idx}' if torch.cuda.is_available() else 'cpu'
                    )
                return torch.from_numpy(data.arr).to(device)
            elif data.mode == 'cupy':
                if device_idx is None:
                    device = data.device
                else:
                    device = cp.cuda.Device(device_idx)
                with device:
                    return cp.array(data.arr)
            elif data.mode == 'numpy':
                return data.arr
            else:
                raise ValueError(f'Unknown DeviceArray mode: {data.mode}')
        return data


def recursive_apply_inplace_with_stop(data, func, stop_cond):
    """Recursive performs func on the items of data
    Does operation in-place, i.e. without copying data.
    stops when stopping criterion is satisfied.
    """
    apply = partial(recursive_apply_inplace_with_stop,
                    func=func,
                    stop_cond=stop_cond)
    if (stop_cond(data)):
        return func(data)
    elif isinstance(data, Mapping):
        for k, v in data.items():
            data[k] = apply(v)
        return data
    elif isinstance(data, list):
        for i, v in enumerate(data):
            data[i] = apply(v)
        return data
    elif isinstance(data, tuple):
        raise ValueError('Cannot modify tuple inplace.')
    else:
        # General object/dataclass
        apply(data.__dict__)
        return data


def is_leaf(data):
    return (is_numeric(data)
            or isinstance(data, str)
            or is_array(data))

def is_leaf_or_device_arr(data):
    return is_leaf(data) or isinstance(data, DeviceArray)


#####################
# [Cuda] -> [Numpy] #
#####################

def to_np(data):
    """Converts an input array to a cpu np array if it is
    either a torch tensor or a cupy array"""
    if isinstance(data, torch.Tensor):
        return data.cpu().numpy()
    elif (cp != np) and isinstance(data, cp.ndarray):
        return data.get()
    return data


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
    def __init__(self, device_idx: Optional[int] = None):
        """
        device_idx = -1 (cpu) or 0+ (gpu)
        """

        self.device_idx = device_idx or -1
        self.use_cuda = torch.cuda.is_available() and self.device_idx >= 0
        self.device = torch.device(
            f'cuda:{self.device_idx}' if self.use_cuda else 'cpu'
        )

    def __call__(self, data):
        if isinstance(data, np.ndarray):
            return torch.from_numpy(data).to(self.device)
        return data


class Np2Cupy:
    def __init__(self, device_idx: Optional[int] = None):
        self.device_idx = device_idx or -1

    def __call__(self, data):
        if isinstance(data, np.ndarray):
            with cp.cuda.Device(self.device_idx):
                return cp.array(data)
        return data

class Np2SingleCudaDevice:
    def __init__(self, device_idx: Optional[int] = None):
        self.device_idx = device_idx or -1
        self.np2cupy = Np2Cupy(self.device_idx)
        self.np2torch = Np2Torch(self.device_idx)

    def __call__(self, data, mode):
        if mode == 'cupy':
            return self.np2cupy(data)
        elif mode == 'torch':
            return self.np2torch(data)
        raise ValueError(f'Unknown mode {mode}')
