"""
https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions
"""

import pytest


def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0


# and if you need to have access to the actual exception info you may use:


def test_recursion_depth():
    with pytest.raises(RuntimeError) as excinfo:

        def f():
            f()

        f()
    assert "maximum recursion" in str(excinfo.value)


def test_foo_not_implemented():
    def foo():
        raise NotImplementedError

    with pytest.raises(RuntimeError) as excinfo:
        foo()
    assert excinfo.type is RuntimeError
