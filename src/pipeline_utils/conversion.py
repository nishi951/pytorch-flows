from collections.abc import Collection, Mapping
from functools import partial

try:
    import cupy
except ImportError:
    pass
import numpy as np
import torch

def recursive_map_np(data, func):
    """Recursively performs func on the items of data
    Only recurses through data that is not np.ndarrays"""
    apply = lambda x: recursive_map_np(x, func)
    if isinstance(data, Mapping):
        return type(data)({k: apply(v) for k, v in data.items()})
    elif isinstance(data, Collection) and not isinstance(data, np.ndarray):
        return type(data)(apply(v) for v in data)
    else:
        return func(data)


def totorch(arr: np.ndarray, device):
    return torch.from_numpy(arr).to(device)


def np2torch(data, runtime):
    device_idx = runtime.device_idx
    use_cuda = torch.cuda.is_available() and device_idx >= 0
    device = torch.device(
        f'cuda:{device_idx}' if use_cuda else 'cpu'
    )
    return recursive_map_np(
        data,
        partial(totorch, device=device)
    )


def tocupy(arr: np.ndarray):
    return cp.array(arr)


def np2cupy(data, runtime):
    with cp.device.Device(runtime.device_idx):
        return recursive_map_np(data, tocupy)
