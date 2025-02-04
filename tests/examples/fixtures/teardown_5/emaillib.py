"""
Teardown/Cleanup (AKA Fixture finalization)

When we run our tests, we’ll want to make sure they clean up after themselves so they don’t mess with any other tests (and also so that we don’t leave behind a mountain of test data to bloat the system). Fixtures in pytest offer a very useful teardown system, which allows us to define the specific steps necessary for each fixture to clean up after itself.

This system can be leveraged in two ways.

"""


class MailAdminClient:
    def create_user(self):
        return MailUser()

    def delete_user(self, user):
        # do some cleanup
        pass


class MailUser:
    def __init__(self):
        self.inbox = []

    def send_email(self, email, other):
        other.inbox.append(email)

    def clear_mailbox(self):
        self.inbox.clear()


class Email:
    def __init__(self, subject, body):
        self.subject = subject
        self.body = body
