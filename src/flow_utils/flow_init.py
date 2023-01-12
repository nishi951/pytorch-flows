#!/usr/bin/env python

from distutils.core import setup, Command
import glob
import os
from pathlib import Path
import shutil

from .path_utils import mkdir_overwrite_or_abort

import tyro

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    CLEAN_FILES = './build ./dist ./*.pyc ./*.tgz ./*.egg-info'.split(' ')

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for path_spec in self.CLEAN_FILES:
            # Make paths absolute and relative to this path
            abs_paths = glob.glob(os.path.normpath(path_spec))
            for path in [str(p) for p in abs_paths]:
                print('removing %s' % os.path.relpath(path))
                shutil.rmtree(path)

def main(
        flow_dir_name: Path = Path('flows'),
):
    """Creates a flow directory, sets the root files, and
    installs a package so that the flow root is findable"""
    mkdir_overwrite_or_abort(flow_dir_name)
    flow_init_file = Path(__file__).parent/'__init__.py'
    shutil.copyfile(src=flow_init_file,
                    dst=Path(flow_dir_name)/'__init__.py')
    setup(
        name="flows-workspace-flow-dir",
        version="0.0.1",
        description="Dummy package so the flow paths are findable.",
        script_args=["develop", "clean"],
        packages=["flows"],
        cmdclass={"clean": CleanCommand}
    )
    print(f'Initialized new flow dir at {flow_dir_name}')

def hook():
    main()

if __name__ == '__main__':
    hook()
