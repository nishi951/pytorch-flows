import hashlib
import json
from pathlib import Path
from typing import Callable

import numpy as np

class NpzCache:
    def __init__(self,
                 filepath: Path,
                 load_callback: Callable = None,
                 store_callback: Callable = None,
    ):
        """
        callbacks are for moving on/off devices, etc.
        """
        self.filepath = filepath
        self.load_callback = load_callback or (lambda x: x)
        self.store_callback = store_callback or (lambda x: x)

    def load(self, func, args, kwargs):
        if not Path(self.filepath).is_file():
            return None
        id_ = self.gen_id(func, args, kwargs)
        data = np.load(self.filepath, allow_pickle=True)
        if id_ in data:
            return self.load_callback(data[id_])
        return None

    def store(self, func, args, kwargs, output):
        id_ = self.gen_id(func, args, kwargs)
        output = self.store_callback(output)
        np.savez_compressed(self.filepath, **{id_: output})

    def gen_id(self, func, args, kwargs):
        return f'{func.__name__}({self.hash_data((args, kwargs))})'

    @staticmethod
    def hash_data(data):
        data_md5 = hashlib.md5(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()
        return data_md5

    def __repr__(self):
        return f'{self.__class__.__name__}({self.filepath})'
