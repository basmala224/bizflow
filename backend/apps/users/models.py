from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model — extended with company/role/profile fields in Part 2."""
