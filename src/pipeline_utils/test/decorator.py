from dataclasses import dataclass
from pathlib import Path

import numpy as np
import tyro

from pipeline_utils.pipeline_decorator import DataPipeline
from pipeline_utils.cache import NpzCache

@dataclass
class Config:
    cache_file: Path = Path(__file__).parent/'./basic_cache.npz'
    """Cache file to store cached results"""
    step3_arg: int = 3


pipeline = DataPipeline()

@pipeline.add(
    deps=[],
    cache=NpzCache('step1.npz',
                   load_callback=lambda x: x.item()),
)
def step1():
    print('Running step 1...')
    return 1


@pipeline.add(
    deps=[step1],
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
