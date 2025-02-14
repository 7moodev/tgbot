# Best Practices

- Follow Naming Conventions
- Test files: test\_<module>.py
- Test functions: test\_<functionality>()
- Use Assertions
- Use assert in pytest, or self.assertEqual() in unittest.
- Test Edge Cases
- Cover normal, boundary, and error conditions.
- Keep Tests Isolated
- Avoid dependencies between tests.
- Use Fixtures (pytest.fixture)
- For reusable setup logic.
- Mock External Dependencies
- Use unittest.mock or pytest-mock.
- Automate Test Running
- Use pytest with tox or pre-commit hooks.
- Continuous Integration (CI)
- Run tests in GitHub Actions, GitLab CI, etc.
- Grouping tests in classes can be beneficial for the following reasons:
  - Test organization
  - Sharing fixtures for tests only in that particular class
  - Applying marks at the class level and having them implicitly apply to all tests

# Knowledge
https://docs.pytest.org/en/stable/how-to/usage.html

- test discovery
    - pytest (see below for other ways to invoke pytest). This will execute all tests in all files whose names follow the form test_*.py or \*_test.py in the current directory and its subdirectories. More generally, pytest follows standard test discovery rules.

- Markers
  - https://docs.pytest.org/en/stable/how-to/mark.html

- Monkeypatching (Mock) modules and environments
  - https://docs.pytest.org/en/stable/how-to/monkeypatch.html

# Libraries
- test runners (such as pytest),
  - https://docs.pytest.org/en/stable/getting-started.html
- linters (e.g., flake8),
- formatters (for example black or isort),
- documentation generators (e.g., Sphinx),
- build and publishing tools (e.g., build with twine),


# Commands

## Specifying which tests to run
- Run tests in a module
pytest test_mod.py

- Run tests in a directory
pytest testing/

- Run tests by keyword expressions
pytest -k 'MyClass and not method'

- To run a specific test within a module:
pytest tests/test_mod.py::test_func

- To run all tests in a class:
pytest tests/test_mod.py::TestClass

- Specifying a specific test method:
pytest tests/test_mod.py::TestClass::test_method

- Specifying a specific parametrization of a test:
pytest tests/test_mod.py::test_func[x1,y2]

- Run tests from packages
pytest --pyargs pkg.testing

## Marks
- Run tests by marker expressions. To run all tests which are decorated with the @pytest.mark.slow decorator:
pytest -m slow

- To run all tests which are decorated with the annotated @pytest.mark.slow(phase=1) decorator, with the phase keyword argument set to 1:
pytest -m "slow(phase=1)"

## Read arguments from file
(Added in version 8.2.)

- All of the above can be read from a file using the @ prefix:

pytest @tests_to_run.txt

- where tests_to_run.txt contains an entry per line, e.g.:
```
tests/test_file.py
tests/test_mod.py::test_func[x1,y2]
tests/test_mod.py::TestClass
-m slow
```

## Profiling test execution duration
- To get a list of the slowest 10 test durations over 1.0s long:
pytest --durations=10 --durations-min=1.0

## Managing loading of plugins
- You can early-load plugins (internal and external) explicitly in the command-line with the -p option:
pytest -p mypluginmodule

- To disable loading specific plugins at invocation time, use the -p option together with the prefix no:.
(Example: to disable loading the plugin doctest, which is responsible for executing doctest tests from text files, invoke pytest like this:)
pytest -p no:doctest

## Other ways of calling pytest
- Calling pytest through python -m pytest
  You can invoke testing through the Python interpreter from the command line:
python -m pytest [...]

- Calling pytest from Python code
    You can invoke pytest from Python code directly:
retcode = pytest.main()














- Shows builtin and custom fixtures
pytest --fixtures
