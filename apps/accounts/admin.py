from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("role", "phone", "department")}),
    )
    list_display = ("username", "email", "role", "is_active")
    list_filter = ("role", "is_active")
