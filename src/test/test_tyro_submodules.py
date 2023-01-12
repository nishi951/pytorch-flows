from dataclasses import dataclass, field, asdict
from typing import List, Optional, Type, Union

import tyro
from tyro.conf import AvoidSubcommands

from config_utils.registry import registry

"""
A simple proof-of-concept demonstrating the power of the registry
in conjunction with tyro.

Note that removing all @registry decorators leaves
perfectly functional python code. (the main function would need to be updated)

In the config, listing a submodule's config will result
in the function receiving an instantiated version
of that submodule with the config applied to it.

E.g. In LossConfig below,, if type(module) is
LossModule1Config, then Loss's constructor will be called as
Loss(lam=lam, module=LossModule1(**[LossModule1Config instance].__dict__))

Finally, functions can also be decorated with configs. Because function
naming conventions are different than class naming conventions, the optional
name argument for register_with_config can come in handy.
"""


@dataclass
class LossModule1Config:
    p1: int
    p2: float


@dataclass
class LossModule2Config:
    p1: int
    p2: float
    p3: List[float]


@dataclass
class LossConfig:
    lam: float
    # Can also set to be optional, aka
    # module: Optional[Union[LossModule1Config, LossModule2Config]] = None

    module: AvoidSubcommands[Union[LossModule1Config, LossModule2Config]]

# register_with_config will expect the config dataclass
# to be named [module name]Config
# Everything gets registered with config by default


@registry.register_with_config
class LossModule1:
    def __init__(
            self,
            p1,
            p2,
    ):
        self.p1 = p1
        self.p2 = p2


@registry.register_with_config
class LossModule2:
    def __init__(
            self,
            p1, p2, p3,
    ):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3


@registry.register_with_config('LossConfig')
class Loss:
    def __init__(
            self,
            lam: float,
            module: Union[LossModule1, LossModule2],
    ):
        """
        """
        self.lam = lam
        self.loss_module = module


if __name__ == '__main__':
    loss_config = tyro.cli(LossConfig)
    loss_fn = registry.configure_submodules(loss_config)
    print(loss_fn)
    print(loss_fn.loss_module)
