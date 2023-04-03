from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from easydict import EasyDict
import matplotlib.pyplot as plt
import numpy as np
import tyro

from pipeline_utils.pipeline import DataPipeline
from pipeline_utils.cache import NpzCache

@dataclass
class Config:
    targets: list[str] = field(default_factory=list)
    reruns: list[str] = field(default_factory=list)
    device_idx: int = 0
    step3_arg: int = 3


pipeline = DataPipeline()

def extract_singleton(data, runtime):
    return data.item()

@pipeline.add(
    deps=[],
    cache=NpzCache('step1.npz',
                   load_callback=extract_singleton),
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
                   load_callback=extract_singleton),
)
def step2(step1: int):
    print(f'Running step 2... (received step1: {step1})')
    return step1 + 3


@pipeline.add(
    deps=[step1a, step2, step1b],
    cache=NpzCache('step3.npz',
                   load_callback=extract_singleton),
)
def step3(step1a: int, step2: int, step1b: int, step3_arg:int):
    print(f'Running step 3... (received step1: {step1a} and step2: {step2} and step1b: {step1b})')
    return step1a + step2 + step1b + step3_arg


@pipeline.add(deps=[step3])
def step4a(step3):
    print(f'Running step 4a... (received step3: {step3})')
    return

@pipeline.add(deps=[step2])
def step4b(step2):
    print(f'Running step 4b... (received step2: {step2})')
    return

def main():
    opt = tyro.cli(Config)
    runtime = EasyDict({
        'device_idx': opt.device_idx,
    })
    pipeline.setup(opt, runtime)
    pipeline.visualize()

    step1a_out = step1a()
    step1b_out = step1b()
    step2_out = step2(step1a_out)
    step3_out = step3(step1a_out, step2_out, step1b_out, opt.step3_arg)

    step4a(step3_out)
    step4b(step2_out)


if __name__ == '__main__':
    main()
