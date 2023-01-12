# pytorch-flows
Package for easily managing multiple experiments or experiment variations

## Installation
Pip install this repo from git with:
`$ pip install "flows-workspace @ git+ssh://git@github.com/nishi951/pytorch-flows.git"`

## Flow Commands
### `flow_init`
The first time you create a flow, run `$ flow_init`
from the project root. This does several things:
1. It creates a directory (called `flows`) be default.
2. It copies a file called `__init__.py` from the install folder that contains 
   various paths that are useful for managing results.
3. It installs `flows` as a new package so that the paths in the `__init__.py` 
   will be visible from everywhere.
4. It deletes the misc stuff that installing a package creates (e.g. `*.egg-info*`)

### `flow_create`
From the `src` dir, run `flow_create --name [exp name]` (`--help` for options)
- Create a new, blank experiment, copied from the experiment at 
  `site-packages/flow_utils/template_exp`.
- Can also copy the existing state of another experiment to a new experiment

## Recommended Project Structure
- `flows`: all experiments, each one in a separate dir
  - `exp1`
  - `exp2`
- `logs`: all results
- `data`: shared (raw) data for all experiments
  - NEVER modify raw data! All modifications should result in experiment-specific data
  - Also may include processed data, or scripts to download datasets programmatically

## Configuration with tyro+registry
By default, `tyro` is used for configuring experiment runs. `tyro` brings with it
some amazing functionality that, when combined with a [registry pattern](https://subscription.packtpub.com/book/programming/9781785885990/5/ch05lvl1sec38/registry-pattern), is incredibly 
useful.

### Registering an object
We begin by importing the registry object

``` python
from config_utils.registry import registry
```

Then, to register an object, we call

``` python
@registry.register
class SomeObject:
    ...
```

Later, from another file or module, we can access the object via

``` python
class_object = registry._clsname2cls['SomeObject']
```

### Registering an object with a config and configuring via tyro
We may need to configure an object and push its parameters to the command line.
To do this, we create a dataclass that mirrors the signature of the class we want to configure.

The naming convention for `register_with_config` is to have the associated dataclass be named `[module name]Config`.

`register_with_config` also takes an optional argument if you want to specify the name of the config object directly. This is useful if we want to register a *function* with a config instead of an object.

``` python
from dataclasses import dataclass

@dataclass
class LossModule1Config:
    p1: int
    p2: float

@registry.register_with_config
class LossModule1:
    def __init__(
            self,
            p1,
            p2,
    ):
        self.p1 = p1
        self.p2 = p2
```

Since the registry knows that `LossModule1Config` is registered to `LossModule1`, We can configure and instantiate `LossModule1` using a command-line interface with
``` python
loss_config = tyro.cli(LossModule1Config)
loss_module = registry.configure_submodules(loss_config)
```

If we had used a function instead of an object instead, the output of `configure_submodules` would be the return value 
of the function.

### Registering nested configurable objects
The beauty of tyro is that we can nest configurable objects and `configure_submodules` will automatically instantiate
and configure them, all with the appropriate command line arguments.

See `src/test/test_tyro_submodules.py` for an example of such behavior.
