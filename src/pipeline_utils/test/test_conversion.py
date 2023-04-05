from dataclasses import dataclass, field
from easydict import EasyDict
from pprint import pprint
import numpy as np
import torch

from pipeline_utils.conversion import (
    to_nested_mapping,
    recursive_apply_inplace_with_stop,
    DeviceArray,
    is_leaf,
    is_leaf_or_device_arr,
)
# from pipeline_utils.conversion import np2torch


def test_np2stuff_basic():
    runtime = EasyDict({
        'device_idx': -1
    })
    a = np.array([1., 2., 3])
    # a_cp = np2cupy(a, runtime)
    # print(a_cp)
    # print(a_cp.Device)

    a_th = np2torch(a, runtime)
    print(a_th)
    print(a_th.device)


def test_np2stuff_recursive():
    runtime = EasyDict({
        'device_idx': -1
    })
    data = {
        'a': np.array([1., 2., 3]),
        'b': (np.array([4., 5., 6.]),
              np.array([7., 8., 9.])),
    }

    # data_cp = np2cupy(data, runtime)
    # print(data_cp)

    data_th = np2torch(data, runtime)
    print(data_th)


@dataclass
class TestDataClass:
    var1: int = 2
    var2: str = 9
    var3: dict = field(default_factory=dict)

def test_dataclass_mapping():
    arr = np.array([1., 2., 3.])
    data = TestDataClass(var3=arr)
    data2 = to_nested_mapping(data)



@dataclass
class TestArrDataClass:
    var1: np.ndarray
    var2: torch.Tensor

def test_recursive_apply_inplace_with_stop():
    data = {
        'a': np.array([1., 2., 3.]),
        'b': [
            np.array([4., 5., 6.]),
            np.array([7., 8., 9.])
        ],
        'c': TestArrDataClass(
            var1=np.array([10., 11.]),
            var2=torch.tensor([12., 13.])
        ),
        'd': ['uhoh', 5, [10]]

    }

    pprint(data)

    recursive_apply_inplace_with_stop(
        data, DeviceArray.infer, is_leaf
    )

    pprint(data)

    recursive_apply_inplace_with_stop(
        data, DeviceArray.unpack, is_leaf_or_device_arr
    )

    pprint(data)



if __name__ == '__main__':
    # test_np2stuff_basic()
    # test_np2stuff_recursive()
    # test_dataclass_mapping()
    test_recursive_apply_inplace_with_stop()
