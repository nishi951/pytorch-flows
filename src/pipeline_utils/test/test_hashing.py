import hashlib
import metrohash
import json
import struct

import numpy as np

from pipeline_utils.cache import hash_data, recursive_hash
from pipeline_utils.conversion import to_nested_mapping

class TestClass:
    def __init__(self, var):
        self.var = var

def binary(num):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))

def test_class_hashing():
    inst1 = TestClass(1)
    print(inst1.__dict__)
    inst2 = TestClass(2)
    print(inst2.__dict__)
    inst3 = TestClass(1)
    print(inst3.__dict__)

    print(hash_data(inst1))
    print(hash_data(inst2))
    print(hash_data(inst3))


    assert hash_data(inst1) == hash_data(inst3)

def test_array_hashing():
    arr = np.array(1.)
    print(arr.dtype)
    print(arr.view('int64'))
    arr_hash = hash_data(arr)


    arr2 = (arr.view('int64') + 1).view('float64')

    print(arr2.view('int64'))
    arr2_hash = hash_data(arr2)
    print(arr2_hash)

    print(arr == arr2)


def test_class_with_array_hashing():
    arr = np.array(1.)
    inst1 = TestClass(arr)

    arr2 = np.array(2.)
    inst2 = TestClass(arr2)

    arr3 = np.array([1., 2])
    inst3 = TestClass(arr3)

    inst1_hash = hash_data(inst1)
    inst2_hash = hash_data(inst2)
    inst3_hash = hash_data(inst3)

    print(inst1_hash)
    print(inst2_hash)
    print(inst3_hash)

def test_metrohashing():
    arr = np.array(1.)
    inst1 = TestClass(arr)

    arr2 = np.array(2.)
    inst2 = TestClass(arr2)

    arr3 = np.array(1.)
    inst3 = TestClass(arr3)

    hash_obj = metrohash.MetroHash64()
    hash_obj = recursive_hash(to_nested_mapping(inst1), hash_obj)
    print(hash_obj.hexdigest())
    # inst2_hash = hash_data(to_nested_mapping(inst2))
    # inst3_hash = hash_data(to_nested_mapping(inst3))

    hash_obj = metrohash.MetroHash64()
    hash_obj = recursive_hash(to_nested_mapping(inst3), hash_obj)
    print(hash_obj.hexdigest())
    # print(inst1_hash)
    # print(inst2_hash)
    # print(inst3_hash)

if __name__ == '__main__':
    test_class_hashing()
    test_array_hashing()
    test_class_with_array_hashing()
    test_metrohashing()
