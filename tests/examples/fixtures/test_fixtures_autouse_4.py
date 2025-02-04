import pytest

"""
Autouse fixtures (fixtures you don’t have to request)

Sometimes you may want to have a fixture (or even several) that you know all your tests will depend on. “Autouse” fixtures are a convenient way to make all tests automatically request them. This can cut out a lot of redundant requests, and can even provide more advanced fixture usage (more on that further down).

We can make a fixture an autouse fixture by passing in autouse=True to the fixture’s decorator. Here’s a simple example for how they can be used:

https://docs.pytest.org/en/stable/how-to/fixtures.html#autouse-fixtures-fixtures-you-don-t-have-to-request
"""


@pytest.fixture
def first_entry():
    return "a"


@pytest.fixture
def order(first_entry):
    return []


@pytest.fixture(autouse=True)
def append_first(order, first_entry):
    return order.append(first_entry)


def test_string_only(order, first_entry):
    assert order == [first_entry]


def test_string_and_int(order, first_entry):
    order.append(2)
    assert order == [first_entry, 2]
