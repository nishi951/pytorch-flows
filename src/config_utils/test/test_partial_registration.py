from dataclasses import dataclass, field
import functools

from config_utils.registry import registry


@dataclass
class MyClassConfig:
    a: int
    b: int

@registry.register_with_config
class MyClass:
    def __init__(self, a: int, b: int, c: float):
        self.abc = a*b*c

@dataclass
class Config:
    my_class: MyClassConfig


def test_partial_register():
    opt = Config(my_class=MyClassConfig(a=1, b=2))
    opt = registry.configure_submodules(opt)

    assert isinstance(opt.my_class, functools.partial)
    opt.my_class = opt.my_class(c=3.)
    assert opt.my_class.abc == 6.


@dataclass
class MyClass2Config:
    a: int
    b: int
    c: float

@registry.register_with_config
class MyClass2:
    def __init__(self, a: int, b: int, c: float):
        self.abc = a*b*c

@dataclass
class Config2:
    my_class2: MyClass2Config

def test_full_register():
    opt = Config2(my_class2=MyClass2Config(a=1, b=2, c=3.))
    opt = registry.configure_submodules(opt)

    assert isinstance(opt.my_class2, MyClass2)
    assert opt.my_class2.abc == 6.
    breakpoint()

if __name__ == '__main__':
    test_partial_register()
    test_full_register()
