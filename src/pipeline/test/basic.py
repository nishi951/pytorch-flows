from dataclasses import dataclass
from pathlib import Path

import tyro

from pipeline import DAG


def step1():
    print('Running step 1...')
    return 1

def step2(step1: int):
    print(f'Running step 2... (received step1: {step1})')
    return step1 + 3

def step3(step1: int, step2: int):
    print(f'Running step 3... (received step1: {step1} and step2: {step2})')
    return step1 + step2

@dataclass
class Config:
    cache_file: Path = Path(__file__).parent/'./basic_cache.npz'
    """Cache file to store cached results"""
    force_recompute: dict = {}
    """"""


def main():
    # Parse cache location
    opt = tyro.cli(Config)
    pipeline = DAG(cache_file=opt.cache_file)

    step1_node = pipeline.add_node(step1)
    step2_node = pipeline.add_node(step2,
                                   kwargs={'step1': step1_node.output},
                                   deps=[step1_node])
    step3_node = pipeline.add_node(step3,
                                   args=(step1_node.output, step2_node.output),
                                   deps=[step1_node,
                                         step2_node])

    pipeline.plot()

    pipeline.load_cache()
    pipeline.compute()

if __name__ == '__main__':
    main()
