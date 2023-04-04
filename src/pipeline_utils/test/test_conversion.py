from easydict import EasyDict
import numpy as np

from pipeline_utils.conversion import np2torch


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

if __name__ == '__main__':
    test_np2stuff_basic()
    test_np2stuff_recursive()
