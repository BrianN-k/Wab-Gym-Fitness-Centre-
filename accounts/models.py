from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("receptionist", "Receptionist"),
        ("accountant", "Accountant"),
        ("coach", "Coach"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="receptionist",
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_receptionist(self):
        return self.role == "receptionist"

    @property
    def is_accountant(self):
        return self.role == "accountant"

    @property
    def is_coach(self):
        return self.role == "coach"