from dataclasses import dataclass, field
from typing import Union, List, Tuple, Optional

import tyro

from flow_utils import SRC_ROOT
from flow_utils.path_utils import ExpPathManager

@dataclass
class ExperimentConfig:
    paths: ExpPathManager = field(
        default_factory=lambda: ExpPathManager(
            ExpPathManager.file2name(
                __file__,
                rel_dir=SRC_ROOT,
            )
        )
    )

def main(config: ExperimentConfig):
    print(config)

if __name__ == '__main__':
    tyro.cli(main)
