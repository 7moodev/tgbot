"""
Request a unique temporary directory for functional tests
pytest provides Builtin fixtures/function arguments to request arbitrary resources, like a unique temporary directory:

List the name tmp_path in the test function signature and pytest will lookup and call a fixture factory to create the resource before performing the test function call. Before the test runs, pytest creates a unique-per-test-invocation temporary directory:

More info on temporary directory handling is available at Temporary directories and files.

Find out what kind of builtin pytest fixtures exist with the command:

pytest --fixtures   # shows builtin and custom fixtures

Note that this command omits fixtures with leading _ unless the -v option is added.
"""


def test_needsfiles(tmp_path):
    print(tmp_path)
    assert 0


# pytest -q test_tmp_path.py
