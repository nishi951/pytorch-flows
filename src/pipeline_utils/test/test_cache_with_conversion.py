from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

import numpy as np
import torch

from pipeline_utils.cache import PklCache


@dataclass
class TestData:
    var1: np.ndarray
    var2: torch.Tensor

@dataclass
class Result:
    res1: np.ndarray
    res2: torch.Tensor

def test_fn(a: np.ndarray, b: torch.Tensor, c: TestData):
    out = {'a+var1': a + c.var1,
           'b+var2': b + c.var2
           }
    return [out, 'yes', Result(res1=-a - c.var1,
                               res2=-b - c.var2)]

def test_full():
    func = test_fn
    a = np.array([1., 2., 3])
    b = torch.tensor([4., 5., 6])
    c = TestData(
        var1=np.array([6*1j,7*1j, 8*1j]),
        var2=torch.tensor([3, 3, 3])
    )
    args = (a, b, c)
    kwargs = {}
    output = func(a, b, c)


    pprint(output)
    # Apply cache
    cache = PklCache(name='test_cache_with_conversion.pkl',
                     cache_dir=Path('cache'))

    cache.store((func, args, kwargs, output))

    output2 = cache.load((func, args, kwargs))

    pprint(output2)

    eq_args = ()
    eq_kwargs = OrderedDict({
        'a': a,
        'b': b,
        'c': c
    })


    output3 = cache.load((func, eq_args, eq_kwargs))
    pprint(output3) # should give None



if __name__ == '__main__':
    test_full()
