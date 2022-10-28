import dataclasses
from typing import Annotated, Union

import tyro


@dataclasses.dataclass(frozen=True)
class CheckoutArgs:
    """Checkout a branch."""
    branch: str


@dataclasses.dataclass(frozen=True)
class CommitArgs:
    """Commit changes."""

    message: str
    all: bool = False


@dataclasses.dataclass
class Args:
    # A union over nested structures, but without subcommand generation. When a default
    # is provided, the type is simply fixed to that default.
    union_without_subcommand: tyro.conf.AvoidSubcommands[
        Union[CheckoutArgs, CommitArgs]
    ]


if __name__ == "__main__":
    print(tyro.cli(Args))
