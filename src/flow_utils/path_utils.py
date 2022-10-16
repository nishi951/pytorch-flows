from dataclasses import dataclass
from pathlib import Path

from flow_utils import SRC_ROOT, LOGS_ROOT

@dataclass
class ExpPathManager:
    # Name of this experiment
    name: str

    @staticmethod
    def file2name(filepath, rel_dir=None):
        """Converts a full filename (usually __file__)
        string to the name of the file without .py

        Optional argument:
        rel_dir - defaults to '.' otherwise, return the relative path
        of current file from rel_dir
        ex:
        if __file__ is /a/b/c/d.py and reL_dir is /a/b,
        then returns c/d

        Example:
        print(__file__) #
        print(os.path.basename(__file__))
        print(os.path.basename(__file__).partition('.py')[0])


        Output:
        /home/mark/projects/isa_nlos/flows/point_est_2d/experiments/mnist_6.py
        mnist_6.py
        mnist_6
        """
        if rel_dir is not None:
            return filepath.partition(
                str(rel_dir) + '/'
            )[-1].partition('.py')[0]
        return os.path.basename(str(filepath)).partition('.py')[0]

    @property
    def exp_path(self) -> Path:
        return SRC_ROOT/self.name

    @property
    def log_dir(self) -> Path:
        return LOGS_ROOT/self.name

    def __repr__(self):
        return repr({self.__class__.__name__: {
            'name': self.name,
            'log_dir': self.log_dir,
            'exp_path': self.exp_path,
        }})
