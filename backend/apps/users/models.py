from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.companies.models import Company

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        EMPLOYEE = 'EMPLOYEE', 'Employee'

    username = None
    email = models.EmailField(unique=True)

    company = models.ForeignKey(
        Company,
        related_name='users',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Null only for SUPER_ADMIN platform accounts.',
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    phone = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(upload_to='users/photos/', null=True, blank=True)
    position = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return self.email
