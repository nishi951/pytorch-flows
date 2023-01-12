from dataclasses import dataclass
from pathlib import Path
import sys
import shutil

def mkdir_overwrite_or_abort(root_path: str, yes: bool = False):
    """
    root_path should be a pathlib.Path
    """
    if root_path.exists():
        # Overwrite?
        if yes:
            shutil.rmtree(root_path)
        else:
            yn = input(
                f'{root_path} exists. Overwrite? [y/n] '
            ).lower()
            if yn == 'y':
                shutil.rmtree(root_path)
            else:
                print('Aborting.')
                sys.exit()
    Path(root_path).mkdir(parents=True, exist_ok=True)
