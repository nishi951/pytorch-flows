from dataclasses import dataclass
from easydict import EasyDict
import numpy as np
import torch
try:
    import cPickle as pickle
except ImportError:
    import pickle

from pipeline_utils.conversion import recursive_map

cache_dir = 'cache'

def test_savez_compressed():
    tests = EasyDict()
    tests.arr = np.array([1., 2., 3.])
    tests.adict = {'a': tests.arr, 'b': 'blah'}
    tests.atuple = (tests.arr, 2*tests.arr)
    tests.atuple2 = ('blahblah', 'blahblahblah')
    tests.atuple3 = (10, 11, 12)


    for k, struct in tests.items():
        filepath = f'{cache_dir}/{k}.npz'
        np.savez_compressed(filepath, data=struct)
        data2 = np.load(filepath, allow_pickle=True)
        breakpoint()
        recursive_map(data2['data'], lambda x: print(type(x)))

def test_save():
    tests = EasyDict()
    tests.arr = np.array([1., 2., 3.])
    tests.adict = {'a': tests.arr, 'b': 'blah'}
    arr2 = np.array([4., 5., 6., 7])
    tests.atuple = [tests.arr, arr2]
    tests.atuple2 = ('blahblah', 'blahblahblah')
    tests.atuple3 = (10, 11, 12)


    for k, struct in tests.items():
        filepath = f'{cache_dir}/{k}.npy'
        np.save(filepath, struct, allow_pickle=True)
        data2 = np.load(filepath, allow_pickle=True)
        breakpoint()
        # recursive_map(data2['data'], lambda x: print(type(x)))

def test_pickle():
    tests = EasyDict()
    tests.arr = np.array([1., 2., 3.])
    tests.adict = {'a': tests.arr, 'b': 'blah'}
    tests.atuple = [tests.arr, 2*tests.arr]
    tests.atuple2 = ('blahblah', 'blahblahblah')
    tests.atuple3 = (10, 11, 12)
    tests.atuple4 = (tests.arr, torch.tensor(tests.arr))

    for k, struct in tests.items():
        filepath = f'{cache_dir}/{k}.pkl'
        with open(filepath, 'wb') as f:
            pickle.dump(struct, f, protocol=pickle.HIGHEST_PROTOCOL)

        with open(filepath, 'rb') as f:
            data2 = pickle.load(f)
            breakpoint()


if __name__ == '__main__':
    # test_savez_compressed()
    # test_save()
    test_pickle()
