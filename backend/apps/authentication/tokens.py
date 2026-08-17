from django.contrib.auth.tokens import PasswordResetTokenGenerator


class PasswordResetTokenGeneratorWithEmail(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f'{user.pk}{user.password}{timestamp}{user.email}'


password_reset_token = PasswordResetTokenGeneratorWithEmail()
