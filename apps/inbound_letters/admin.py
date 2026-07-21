from django.contrib import admin

from .models import Assignment, InboundLetter, Sender


@admin.register(Sender)
class SenderAdmin(admin.ModelAdmin):
    list_display = ("name", "institution", "contact")
    search_fields = ("name", "institution")


@admin.register(InboundLetter)
class InboundLetterAdmin(admin.ModelAdmin):
    list_display = ("tracking_code", "title", "sender", "status", "received_date")
    list_filter = ("status", "received_date")
    search_fields = ("tracking_code", "title", "original_ref_no")
    readonly_fields = ("tracking_code", "received_date")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("letter", "assigned_to", "status", "due_date")
    list_filter = ("status",)
    search_fields = ("letter__tracking_code", "assigned_to__username")
