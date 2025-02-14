"""
Safe fixture structure

The safest and simplest fixture structure requires limiting fixtures to only making one state-changing action each, and then bundling them together with their teardown code, as the email examples above showed.

The chance that a state-changing operation can fail but still modify state is negligible, as most of these operations tend to be transaction-based (at least at the level of testing where state could be left behind). So if we make sure that any successful state-changing action gets torn down by moving it to a separate fixture function and separating it from other, potentially failing state-changing actions, then our tests will stand the best chance at leaving the test environment the way they found it.

For an example, let’s say we have a website with a login page, and we have access to an admin API where we can generate users. For our test, we want to:

    Create a user through that admin API

    Launch a browser using Selenium

    Go to the login page of our site

    Log in as the user we created

    Assert that their name is in the header of the landing page

We wouldn’t want to leave that user in the system, nor would we want to leave that browser session running, so we’ll want to make sure the fixtures that create those things clean up after themselves.

Here’s what that might look like:

Note

For this example, certain fixtures (i.e. base_url and admin_credentials) are implied to exist elsewhere. So for now, let’s assume they exist, and we’re just not looking at them.

"""

from uuid import uuid4
from urllib.parse import urljoin

from selenium.webdriver import Chrome
import pytest

from src.utils.pages import LoginPage, LandingPage
from src.utils import AdminApiClient
from src.utils.data_types import User


@pytest.fixture
def admin_client(base_url, admin_credentials):
    return AdminApiClient(base_url, **admin_credentials)


@pytest.fixture
def user(admin_client):
    _user = User(name="Susan", username=f"testuser-{uuid4()}", password="P4$$word")
    admin_client.create_user(_user)
    yield _user
    admin_client.delete_user(_user)


@pytest.fixture
def driver():
    _driver = Chrome()
    yield _driver
    _driver.quit()


@pytest.fixture
def login(driver, base_url, user):
    driver.get(urljoin(base_url, "/login"))
    page = LoginPage(driver)
    page.login(user)


@pytest.fixture
def landing_page(driver, login):
    return LandingPage(driver)


def test_name_on_landing_page_after_login(landing_page, user):
    assert landing_page.header == f"Welcome, {user.name}!"


"""
The way the dependencies are laid out means it’s unclear if the user fixture would execute before the driver fixture.
But that’s ok, because those are atomic operations, and so it doesn’t matter which one runs first because the sequence of events for the test is still linearizable.
But what does matter is that, no matter which one runs first, if the one raises an exception while the other would not have, neither will have left anything behind.
If driver executes before user, and user raises an exception, the driver will still quit, and the user was never made.
And if driver was the one to raise the exception, then the driver would never have been started and the user would never have been made.
"""
