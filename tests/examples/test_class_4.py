"""
Group multiple tests in a class
Once you develop multiple tests, you may want to group them into a class. pytest makes it easy to create a class containing more than one test:

pytest discovers all tests following its Conventions for Python test discovery, so it finds both test_ prefixed functions. There is no need to subclass anything, but make sure to prefix your class with Test otherwise the class will be skipped. We can simply run the module by passing its filename:

The first test passed and the second failed. You can easily see the intermediate values in the assertion to help you understand the reason for the failure.

Grouping tests in classes can be beneficial for the following reasons:

        Test organization

        Sharing fixtures for tests only in that particular class

        Applying marks at the class level and having them implicitly apply to all tests


"""


class TestClass:
    def test_one(self):
        x = "this"
        assert "h" in x

    def test_two(self):
        x = "hello"
        assert hasattr(x, "check")


# pytest -q test_class.py
