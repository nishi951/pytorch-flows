from dataclasses import dataclass
from typing import Annotated, Union

import tyro
from tyro.conf import subcommand

@dataclass(frozen=True)
class SubModule1Config:
    param1: float
submod1_defaults = {
    'basic': SubModule1Config(param1=1.),
    'fancy': SubModule1Config(param1=2.2),
}
submod1_descriptions = {
    'basic': 'Basic config',
    'fancy': 'Fancy config'
}
SubModule1DefaultsType = tyro.extras.subcommand_type_from_defaults(
    submod1_defaults, submod1_descriptions
)

@dataclass(frozen=True)
class SubModule2Config:
    param2: int
submod2_defaults = {
    'basic': SubModule2Config(param2=0),
    'fancy': SubModule2Config(param2=-5),
}
submod2_descriptions = {
    'basic': 'Basic config',
    'fancy': 'Fancy config'
}
SubModule2DefaultsType = tyro.extras.subcommand_type_from_defaults(
    submod2_defaults, submod2_descriptions
)

@dataclass
class FullModuleConfig:
    sub1: Union[
        Annotated[
            SubModule1Config,
            subcommand('manual', description='Manual')
        ],
        SubModule1DefaultsType,
    ]

    sub2: Union[
        Annotated[
            SubModule2Config,
            subcommand('manual', description='Manual')
        ],
        SubModule2DefaultsType,
    ]

if __name__ == '__main__':
    full_module_config = tyro.cli(FullModuleConfig)
    print(full_module_config)
