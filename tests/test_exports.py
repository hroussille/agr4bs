import pytest
import agr4bs
from types import ModuleType


def test_main_package():
    print(agr4bs)
    assert isinstance(agr4bs, ModuleType);
