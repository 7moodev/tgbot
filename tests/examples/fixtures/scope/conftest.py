"""
Scope: sharing fixtures across classes, modules, packages or session

Fixtures requiring network access depend on connectivity and are usually time-expensive to create. Extending the previous example, we can add a scope="module" parameter to the @pytest.fixture invocation to cause a smtp_connection fixture function, responsible to create a connection to a preexisting SMTP server, to only be invoked once per test module (the default is to invoke once per test function). Multiple test functions in a test module will thus each receive the same smtp_connection fixture instance, thus saving time. Possible values for scope are: function, class, module, package or session.

The next example puts the fixture function into a separate conftest.py file so that tests from multiple test modules in the directory can access the fixture function:
"""

"""
Fixture scopes

Fixtures are created when first requested by a test, and are destroyed based on their scope:

    function: the default scope, the fixture is destroyed at the end of the test.

    class: the fixture is destroyed during teardown of the last test in the class.

    module: the fixture is destroyed during teardown of the last test in the module.

    package: the fixture is destroyed during teardown of the last test in the package where the fixture is defined, including sub-packages and sub-directories within it.

    session: the fixture is destroyed at the end of the test session.

"""

import smtplib

import pytest


@pytest.fixture(scope="module")
def smtp_connection():
    return smtplib.SMTP("smtp.gmail.com", 587, timeout=5)


@pytest.fixture(scope="session")
def smtp_connection():
    # the returned fixture value will be shared for
    # all tests requesting it
    ...
