from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        a = six.text_type(user.pk)
        b = six.text_type(timestamp)
        c = six.text_type(user.email_confirmed)
        return (a + b + c)

account_activation_token = AccountActivationTokenGenerator()