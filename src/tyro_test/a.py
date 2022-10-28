from dataclasses import dataclass
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
SubModuleADefaultsType = tyro.extras.subcommand_type_from_defaults(
    submoda_defaults, submoda_descriptions
)

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
SubModuleBDefaultsType = tyro.extras.subcommand_type_from_defaults(
    submodb_defaults, submodb_descriptions
)

@dataclass
class FullModuleConfig:
    suba: SubModuleADefaultsType
    subb: SubModuleBDefaultsType

if __name__ == '__main__':
    full_module_config = tyro.cli(FullModuleConfig)
    print(full_module_config)
