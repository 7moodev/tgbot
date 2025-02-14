from emaillib import Email, MailAdminClient

import pytest

"""
Safe teardowns

The fixture system of pytest is very powerful, but it’s still being run by a computer, so it isn’t able to figure out how to safely teardown everything we throw at it. If we aren’t careful, an error in the wrong spot might leave stuff from our tests behind, and that can cause further issues pretty quickly.

For example, consider the following tests (based off of the mail example from above):
"""

"""
This version is a lot more compact, but it’s also harder to read, doesn’t have a very descriptive fixture name, and none of the fixtures can be reused easily.

There’s also a more serious issue, which is that if any of those steps in the setup raise an exception, none of the teardown code will run.

One option might be to go with the addfinalizer method instead of yield fixtures, but that might get pretty complex and difficult to maintain (and it wouldn’t be compact anymore).

$ pytest -q test_emaillib.py
.                                                                    [100%]
1 passed in 0.12s

"""


@pytest.fixture
def setup():
    mail_admin = MailAdminClient()
    sending_user = mail_admin.create_user()
    receiving_user = mail_admin.create_user()
    email = Email(subject="Hey!", body="How's it going?")
    sending_user.send_email(email, receiving_user)
    yield receiving_user, email
    receiving_user.clear_mailbox()
    mail_admin.delete_user(sending_user)
    mail_admin.delete_user(receiving_user)


def test_email_received(setup):
    receiving_user, email = setup
    assert email in receiving_user.inbox
