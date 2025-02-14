def func(x):
    assert x % 2 == 0, "value was odd, should be even"
    return x + 1


def test_answer():
    assert func(3) == 5
