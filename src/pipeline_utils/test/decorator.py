from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import tyro

from pipeline_utils.pipeline_decorator import DataPipeline
from pipeline_utils.cache import NpzCache

@dataclass
class Config:
    targets: list[str] = field(default_factory=list)
    reruns: list[str] = field(default_factory=list)
    step3_arg: int = 3


pipeline = DataPipeline()


@pipeline.add(
    deps=[],
    cache=NpzCache('step1.npz',
                   load_callback=lambda x: x.item()),
)
def step1a():
    print('Running step 1a...')
    return 1

@pipeline.add(deps=[])
def step1b():
    print('Running step 1b...')
    return 2

@pipeline.add(
    deps=[step1a],
    cache=NpzCache('step2.npz',
                   load_callback=lambda x: x.item()),
)
def step2(step1: int):
    print(f'Running step 2... (received step1: {step1})')
    return step1 + 3

@pipeline.add(
    deps=[step1, step2],
    cache=NpzCache('step3.npz',
                   load_callback=lambda x: x.item()),
)
def step3(step1: int, step2: int, step3_arg:int):
    print(f'Running step 3... (received step1: {step1} and step2: {step2})')
    return step1 + step2 + step3_arg

def main():
    opt = tyro.cli(Config)

    step1_out = step1()
    step2_out = step2(step1_out)
    step3_out = step3(step1_out, step2_out, opt.step3_arg)

    print(step3_out)

if __name__ == '__main__':
    main()
