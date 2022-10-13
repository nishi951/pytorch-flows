from argparse import ArgumentParser
import shutil

from experiments import EXP_ROOT

p = ArgumentParser(description='Experiment manager')
p.add_argument('--name',
               default='exp',
               help='Name of the new experiment (can be nested)')
p.add_argument('--copy_from',
               default='.template_exp',
               help='Copy files from existing experiment')
def mkdir_overwrite_or_abort(root_path, yes=False):
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

def main():
    opt = p.parse_args()

    # Copy over stuff
    shutil.copytree(
        src=opt.copy_from,
        dst=str(EXP_ROOT/opt.name),
    )
    print(f'Copied experiment from {opt.copy_from} to '\
          + f'{str(EXP_ROOT/opt.name)}')

if __name__ == '__main__':
    main()
