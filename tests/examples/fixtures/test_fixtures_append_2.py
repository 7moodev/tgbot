import pytest


# Arrange
@pytest.fixture
def first_entry():
    return "a"


# Arrange
@pytest.fixture
def order(first_entry):
    return [first_entry]


def test_string(order):
    # Act
    order.append("b")

    # Assert
    assert order == ["a", "b"]


"""
A test/fixture can request more than one fixture at a time
https://docs.pytest.org/en/stable/how-to/fixtures.html#a-test-fixture-can-request-more-than-one-fixture-at-a-time
"""


def test_string_more(order, expected_list):
    # Act
    order.append(3.0)

    # Assert
    assert order == expected_list


"""
Fixtures are reusable
"""


def test_int(order):
    # Act
    order.append(2)

    # Assert
    assert order == ["a", 2]
