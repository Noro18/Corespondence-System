from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", CustomUser.Role.ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administradór"
        SEKRETARIADU = "SEK", "Sekretariadu"
        PREZIDENTE = "PREZ", "Prezidente"
        STAFF = "STF", "Funsionáriu"

    role = models.CharField(max_length=5, choices=Role.choices, default=Role.STAFF)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    class Meta:
        db_table = "accounts"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
