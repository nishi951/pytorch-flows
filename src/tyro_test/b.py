from dataclasses import dataclass
from itertools import product
from typing import Annotated, Union

import tyro
from tyro.conf import subcommand

@dataclass(frozen=True)
class SubModuleAConfig:
    param1: float
submoda_defaults = {
    'basic': SubModuleAConfig(param1=1.),
    'fancy': SubModuleAConfig(param1=2.2),
}
submoda_descriptions = {
    'basic': 'Basic config',
    'fancy': 'Fancy config'
}

@dataclass(frozen=True)
class SubModuleBConfig:
    param2: int
submodb_defaults = {
    'basic': SubModuleBConfig(param2=0),
    'fancy': SubModuleBConfig(param2=-5),
}
submodb_descriptions = {
    'basic': 'Basic config',
    'fancy': 'Fancy config'
}

@dataclass
class FullModuleConfig:
    suba: SubModuleAConfig
    subb: SubModuleBConfig

all_defaults = {}
all_descriptions = {}
combos = product(submoda_defaults.items(), submodb_defaults.items())
for (suba_name, suba_config), (subb_name, subb_config) in combos:
    name = f'A{suba_name}_B{subb_name}'
    all_defaults[name] = FullModuleConfig(
        suba=suba_config,
        subb=subb_config,
    )
    all_descriptions[name] = f'A: {submoda_descriptions[suba_name]}, ' \
        + f'B: {submodb_descriptions[subb_name]}'

if __name__ == '__main__':
    full_module_config = tyro.cli(
        tyro.extras.subcommand_type_from_defaults(
            all_defaults,
            all_descriptions,
        )
    )
    print(full_module_config)
