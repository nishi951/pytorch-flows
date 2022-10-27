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
From the `src` dir, run `flow_create --name [exp name]` (`--help` for options)
- Create a new, blank experiment
  - Experiment results will be logged to a corresponding subdir in the `logs` folder
- Can also copy the existing state of another experiment to a new experiment

## Project Structure
- `src`: all code
- `logs`: all results
- `data`: shared (raw) data for all experiments
  - NEVER modify raw data! All modifications should result in experiment-specific data
  - Also may include processed data, or scripts to download datasets programmatically

## Configuration
By default, `tyro` is used for configuring experiment runs.
