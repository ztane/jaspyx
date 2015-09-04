from __future__ import absolute_import, division, print_function
from jaspyx.builtins import BUILTINS


def test_builtins():
    assert isinstance(BUILTINS, dict)
