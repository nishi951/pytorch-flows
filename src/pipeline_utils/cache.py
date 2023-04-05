from abc import ABC, abstractmethod
from collections.abc import Mapping
from functools import partial
import metrohash
import json
from pathlib import Path
from typing import Callable, Optional

try:
    import cPickle as pickle
except ImportError:
    import pickle

import numpy as np

from .conversion import (
    DeviceArray,
    to_nested_mapping,
    to_np,
    recursive_apply_inplace_with_stop,
    is_numeric,
    is_array,
    is_leaf,
    is_leaf_or_device_arr
)


class Cache(ABC):
    @abstractmethod
    def store(self, data):
        return NotImplemented

    @abstractmethod
    def load(self, data):
        return NotImplemented


def recursive_hash(data, hash_fn):
    """hash_fn should be an incremental hash function"""
    if is_numeric(data):
        hash_fn(str(data))
    elif isinstance(data, str):
        hash_fn(data)
    elif is_array(data):
        hash_fn(to_np(data))
    elif isinstance(data, Mapping):
        for k, v in data.items():
            recursive_hash(k, hash_fn)
            recursive_hash(v, hash_fn)
    elif isinstance(data, list) or isinstance(data, tuple):
        for v in data:
            recursive_hash(v, hash_fn)


def hash_data(data):
    hash_obj = metrohash.MetroHash64()
    recursive_hash(
        to_nested_mapping(data),
        hash_obj.update
    )
    return hash_obj.hexdigest()


class PklCache(Cache):
    def __init__(self,
                 name: Optional[str] = None,
                 cache_dir: Optional[Path] = None,
                 load_callback: Optional[Callable] = None,
                 store_callback: Optional[Callable] = None,
    ):
        """

        callbacks are for moving on/off devices, etc.
        """
        self.filename = name or 'cache.pkl'
        self.cache_dir = cache_dir or Path('.')
        self.load_callback = load_callback or (lambda x: x)
        self.store_callback = store_callback or (lambda x: x)

    @property
    def filepath(self) -> Path:
        return self.cache_dir/self.filename

    def store(self, data):
        """Stores as np arrays, even if inputs are ints or strs, etc."""
        func, args, kwargs, output = data
        id_ = self.gen_id(func, args, kwargs)
        # Store output data types (modifies in place)
        output = self.store_callback(output)
        output = recursive_apply_inplace_with_stop(
            output, DeviceArray.infer, is_leaf
        )
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, 'wb') as f:
            pickle.dump({id_: output}, f)

    def load(self, data, device_idx=None):
        func, args, kwargs = data
        if not self.filepath.is_file():
            return None
        id_ = self.gen_id(func, args, kwargs)
        with open(self.filepath, 'rb') as f:
            cached = pickle.load(f)
            if id_ in cached:
                output = cached[id_]
                unpack = partial(DeviceArray.unpack,
                                 device_idx=device_idx)
                output = recursive_apply_inplace_with_stop(
                    output, unpack, is_leaf_or_device_arr
                )
                output = self.load_callback(output)
                return output
        return None

    def gen_id(self, func, args, kwargs):
        return f'{func.__name__}({hash_data([list(args), kwargs])})'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.filepath})'


class NpzCache(Cache):
    """Deprecated in favor of PklCache"""
    def __init__(self,
                 name: Optional[str] = None,
                 cache_dir: Optional[Path] = None,
                 load_callback: Optional[Callable] = None,
                 store_callback: Optional[Callable] = None,
    ):
        """

        callbacks are for moving on/off devices, etc.
        """
        self.filename = name or 'cache.npz'
        self.cache_dir = cache_dir or Path('.')
        self.load_callback = load_callback or (lambda x: x)
        self.store_callback = store_callback or (lambda x: x)

    @property
    def filepath(self) -> Path:
        return self.cache_dir/self.filename

    def load(self, data):
        func, args, kwargs = data
        if not self.filepath.is_file():
            return None
        id_ = self.gen_id(func, args, kwargs)
        cached = np.load(self.filepath, allow_pickle=True)
        if id_ in cached:
            output = cached[id_]
            types = cached[TYPEKEY]
        return None

    def store(self, data):
        """Stores as np arrays, even if inputs are ints or strs, etc."""
        func, args, kwargs, output = data
        id_ = self.gen_id(func, args, kwargs)
        # Store output data types
        types = recursive_map(data, lambda a: (type(a).__name__, devicestr(a)))
        output = recursive_map(data, tonp)
        output = self.store_callback(output)
        assert id_ != TYPEKEY
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(self.filepath, **{id_: output, TYPEKEY: types})


    def gen_id(self, func, args, kwargs):
        return f'{func.__name__}({hash_data((args, kwargs))})'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.filepath})'
