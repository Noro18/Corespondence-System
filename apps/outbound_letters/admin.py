from django.contrib import admin

from .models import ApprovalStage, OutboundLetter


@admin.register(OutboundLetter)
class OutboundLetterAdmin(admin.ModelAdmin):
    list_display = ("tracking_code", "subject", "recipient_institution", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("tracking_code", "subject", "original_ref_no")
    readonly_fields = ("tracking_code", "created_at")


@admin.register(ApprovalStage)
class ApprovalStageAdmin(admin.ModelAdmin):
    list_display = ("letter", "stage", "decision", "reviewer", "decided_at")
    list_filter = ("stage", "decision")
