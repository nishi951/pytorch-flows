from abc import ABC, abstractmethod
from collections.abc import Mapping
import functools
import metrohash
import json
from pathlib import Path
from typing import Callable, Optional

try:
    import cPickle as pickle
except ImportError:
    import pickle

import numpy as np

from .conversion import jsonify, recursive_map, to_nested_mapping, is_array, is_numeric

TYPEKEY = 'type'

class Cache(ABC):
    @abstractmethod
    def load(self, data):
        return NotImplemented

    @abstractmethod
    def store(self, data):
        return NotImplemented


def recursive_hash(data, hash_obj):
    """hash_fn should be an incremental hash function"""
    apply = lambda x, hash_obj: recursive_hash(x, hash_obj)
    if is_numeric(data):
        hash_obj.update(str(data))
    elif isinstance(data, str) or is_array(data):
        hash_obj.update(data)
    elif isinstance(data, Mapping):
        for k, v in data.items():
            recursive_hash(k, hash_obj)
            recursive_hash(v, hash_obj)
    elif isinstance(data, list) or isinstance(data, tuple):
        for v in data:
            recursive_hash(v, hash_obj)
    return hash_obj


def hash_data_json(data):
    jsonified = recursive_map(to_nested_mapping(data), jsonify)
    json_dump = json.dumps(jsonified, sort_keys=True, default=lambda obj: obj.__dict__).encode('utf-8')
    hash_data = metrohash.hash64_int(json_dump)
    return hash_data


def hash_data(data):
    hash_obj = metrohash.MetroHash64()
    hash_obj = recursive_hash(
        to_nested_mapping(data),
        hash_obj
    )
    return hash_obj.hexdigest()


class NpzCache(Cache):
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
        return self._cache_dir/self._filename

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
        return self._cache_dir/self._filename

    def load(self, data):
        func, args, kwargs = data
        if not self.filepath.is_file():
            return None
        id_ = self.gen_id(func, args, kwargs)
        with open(self.filepath, 'rb') as f:
            cached = pickle.load(f)
            if id_ in cached:
                output = cached[id_]
                return output
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

        with open(self.filepath, 'wb') as f:
            pickle.dump({id_: output}, f)

    def gen_id(self, func, args, kwargs):
        return f'{func.__name__}({hash_data((args, kwargs))})'

    @staticmethod

    def __repr__(self):
        return f'{self.__class__.__name__}({self.filepath})'


class HybridCache(Cache):
    """Combines several cache modalities for different
    output types
    """
    def __init__(self, cache_mapping):
        self.cache_mapping = cache_mapping
