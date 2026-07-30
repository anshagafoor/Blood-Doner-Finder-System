from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with role-based access."""

    class Role(models.TextChoices):
        DONOR = "DONOR", "Donor"
        HOSPITAL = "HOSPITAL", "Hospital"
        ORGANIZATION = "ORGANIZATION", "Health Organization"
        ADMIN = "ADMIN", "Administrator"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.DONOR)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_donor(self):
        return self.role == self.Role.DONOR

    @property
    def is_hospital(self):
        return self.role == self.Role.HOSPITAL

    @property
    def is_organization(self):
        return self.role == self.Role.ORGANIZATION

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser
