import numpy as np
from time import perf_counter
import metrohash

from pipeline_utils.cache import hash_data


arr = np.random.randn(1_000_000_000)

def time_hash_data():
    start = perf_counter()
    hash_data(arr)
    total = perf_counter() - start
    print(f'Hash data timing: {total}s')

def time_pure_hash():
    start = perf_counter()
    metrohash.hash64_int(arr)
    total = perf_counter() - start
    print(f'MetroHash timing: {total}s')


def time_pkl():
    pass

def time_npz():
    pass

if __name__ == '__main__':
    time_hash_data()
    time_pure_hash()
