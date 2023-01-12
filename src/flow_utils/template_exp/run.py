from dataclasses import dataclass, field
from typing import Union, List, Tuple, Optional

import tyro

from flows import PROJ_ROOT

@dataclass
class RunConfig:
    name: str
    """Name of this experiment"""

def main(config: RunConfig):
    print(config)

if __name__ == '__main__':
    tyro.cli(main)
