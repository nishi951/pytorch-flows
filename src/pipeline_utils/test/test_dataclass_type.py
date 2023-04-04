from collections.abc import Mapping, Sequence, Container
from dataclasses import dataclass

@dataclass
class TestDataclass:
    a: int = 1
    b: str = 'foo'

def test_dataclasstype():
    test = TestDataclass()
    breakpoint()
    print(isinstance(test, Mapping))

if __name__ == '__main__':
    test_dataclasstype()
