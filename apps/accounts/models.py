from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        SEKRETARIADU = "SEK", "Sekretariadu"
        PREZIDENTE = "PREZ", "Prezidente"
        STAFF = "STF", "Staff"

    role = models.CharField(max_length=5, choices=Role.choices, default=Role.STAFF)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
