#!/usr/bin/env python

from pathlib import Path
import shutil

import tyro

def main(
        name: str,
        copy_from: Path = Path(__file__).parent/'.template_exp',
        copy_to_dir: Path = Path('.'),
):
    # Copy over stuff
    shutil.copytree(
        src=copy_from,
        dst=str(copy_to_dir/name),
    )
    print(f'Copied experiment from {copy_from} to '
          + f'{str(copy_to_dir/name)}')

def hook():
    """Special for project.scripts in pyproject.toml"""
    tyro.cli(main)

if __name__ == '__main__':
    hook()
