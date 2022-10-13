# pytorch-flows
Template repo for quickly starting a new project in the flow style

## Setup
Before setting up, feel free to modify the environment name in environment.yml.

First, install the environment with

``` sh
conda env create -f environment.yml
```

Then, pip install this whole repo with

``` sh
pip install -e .
```

### Creating an experiment
From the `experiment` dir, run `python exp.py` (`--help` for options)
- Create a new, blank experiment
  - Experiment results will be logged to a corresponding subdir in the `logs` folder
- Can also copy the existing state of another experiment to a new experiment

### Experiment structure
`experiments`
- `exp1`
  - Any code files/folders (`*.py`, `src/`, etc.)
    - Can contain multiple different "runs" or configurations of the same ish experiment
  - Preprocessed data (`data/preproc`)
  - Log directories (`logs/`)
  - Notebooks for scratch or visualization (`notebooks/`)
  - Special files:
    - `__init__.py` allowing this experiment to be used as a module
    - `environment.yml` allowing custom modifications if necessary
- `exp2`
- ...

## Project Structure
- `experiments`: one directory per flow
- `core`: shared code for all experiments - use with caution!
- `data`: shared (raw) data for all experiments
  - NEVER modify raw data! All modifications should result in experiment-specific data
