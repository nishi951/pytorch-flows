from dataclasses import dataclass
import functools
import inspect
from typing import Callable, Optional, Type, Union
import warnings

@dataclass
class _Registry:
    """Holds mappings between
    class names to classes,
    config names to config dataclasses,
    config names to class names,
    class names to config names"""
    _clsname2cls = {}
    _cfgname2cfg = {}
    _cfgname2clsname = {}
    _clsname2cfgname = {}

    def register(
            self, cls: Type
    ) -> Type:
        """Register a class without a config"""
        assert callable(cls)
        if cls.__name__ in self._clsname2cls:
            warnings.warn(
                f'{cls.__name__} already in registry,'
                + 'overwriting...'
            )
        self._clsname2cls[cls.__name__] = cls
        return cls

    def register_with_config(
            self, *args
    ) -> Union[Type, Callable[[Type], Type]]:
        """Register a class with a config
        """
        frame = inspect.currentframe()
        try:
            class_context = frame.f_back.f_locals
            class_lookup = {
                k: v for k, v in class_context.items()
                if inspect.isclass(v)
            }
        finally:
            del frame

        def wrapper(cls, config_name):
            try:
                config_class = class_lookup[config_name]
            except KeyError as e:
                print(
                    f'Could not find {config_name} '
                    + f'in class context {class_lookup}'
                )
                raise e
            if cls.__name__ in self._clsname2cls:
                warnings.warn(
                    f'{cls.__name__} already in registry,'
                    + 'overwriting...'
                    )
            self._clsname2cls[cls.__name__] = cls
            self._cfgname2cfg[config_name] = config_class
            self._cfgname2clsname[config_name] = cls.__name__
            self._clsname2cfgname[cls.__name__] = config_name
            return cls

        if len(args) == 1 and callable(args[0]):
            # Called without arguments
            cls = args[0]
            config_name = cls.__name__ + 'Config'
            wrapper(cls, config_name)
            return cls


        elif isinstance(args[0], str):
            # Called with arguments
            config_name = args[0]
            return functools.partial(wrapper, config_name=config_name)
        # Find the config with this name
        else:
            raise ValueError(
                f'Register called on unregistrable object. args: {args}'
            )

    def configure_submodules(self, config):
        """Apply a config to a class"""
        config_dict = config.__dict__
        for k, v in config_dict.items():
            if type(v).__name__ in self._cfgname2clsname:
                # Found an instantiable class
                subconfig = v
                cfgname = type(subconfig).__name__
                clsname = self._cfgname2clsname[cfgname]
                cls = self._clsname2cls[clsname]
                subconfig_dict = self.configure_submodules(subconfig)
                try:
                    config_dict[k] = cls(**subconfig_dict)
                except TypeError as e:
                    print(f'Error when initializing {cls} from config '
                          +f'{type(config).__name__}')
                    raise e
        return config_dict


registry = _Registry()  # Singleton
