from dataclasses import dataclass
from typing import Union

import tyro
from tyro.conf import subcommand

@dataclass(frozen=True)
class SubModule1aConfig:
    param1: float

@dataclass(frozen=True)
class SubModule1bConfig:
    param2: float
    param3: int

@dataclass
class SubModule2aConfig:
    param1: bool

@dataclass
class SubModule2bConfig:
    param2: str
    param3: bool

@dataclass
class FullModuleConfig:
    submodule1: tyro.conf.AvoidSubcommands[Union[
        SubModule1aConfig,
        SubModule1bConfig,
    ]]


if __name__ == '__main__':
    full_module_config = tyro.cli(FullModuleConfig)
    print(full_module_config)
