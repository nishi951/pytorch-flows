from dataclasses import dataclass
from typing import Union
from typing_extensions import Annotated

import tyro
from tyro.conf import subcommand

def tyro_subcommand(T, **subcommand_kwargs):
    """subcommand_kwargs
    name:
    default:
    description:
    prefix_name:
    """
    return Annotated[
        T,
        subcommand(**subcommand_kwargs)
    ]


if __name__ == '__main__':
    @dataclass
    class OptionA:
        arg1: int

    @dataclass
    class OptionB:
        arg1: str
        arg2: float
    subc_type = Union[
        tyro_subcommand(OptionA, name='a1', default=OptionA(1), description='OptionA with 1'),
        tyro_subcommand(OptionA, name='a2', default=OptionA(2), description='OptionA with 2'),
        tyro_subcommand(OptionB, name='bc2', default=OptionB('c', 2.), description='OptionB with c and 2')
    ]
    opt = tyro.cli(subc_type)
    print(opt)
