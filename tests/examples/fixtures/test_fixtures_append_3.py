import pytest

"""
Fixtures can be requested more than once per test (return values are cached)
Fixtures can also be requested more than once during the same test, and pytest won’t execute them again for that test. This means we can request fixtures in multiple fixtures that are dependent on them (and even again in the test itself) without those fixtures being executed more than once.
https://docs.pytest.org/en/stable/how-to/fixtures.html#fixtures-can-be-requested-more-than-once-per-test-return-values-are-cached
"""


# Arrange
@pytest.fixture
def first_entry():
    return "a"


# Arrange
@pytest.fixture
def order():
    return []


# Act
@pytest.fixture
def append_first(order, first_entry):
    return order.append(first_entry)


def test_string_only(append_first, order, first_entry):
    # Assert
    assert order == [first_entry]
