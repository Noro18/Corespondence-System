from django.conf import settings
from django.db import models


class Sender(models.Model):
    name = models.CharField(max_length=255)
    institution = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class InboundLetter(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "REG", "Registered"
        ASSIGNED = "ASN", "Assigned"
        COMPLETED = "CMP", "Completed"
        ARCHIVED = "ARC", "Archived"

    tracking_code = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=255)
    original_ref_no = models.CharField(max_length=100, blank=True)
    sender = models.ForeignKey(Sender, on_delete=models.PROTECT)
    letter_date = models.DateField()
    received_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to="inbound_pdfs/")
    description = models.TextField(blank=True)
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="registered_letters",
    )
    status = models.CharField(
        max_length=3, choices=Status.choices, default=Status.REGISTERED, db_index=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-received_date"]

    def __str__(self):
        return f"{self.tracking_code} - {self.title}"


class Assignment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PND", "Pending"
        IN_PROGRESS = "IPR", "In Progress"
        COMPLETED = "CMP", "Completed"

    letter = models.ForeignKey(
        InboundLetter, on_delete=models.CASCADE, related_name="assignments"
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_tasks",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="my_tasks",
    )
    instructions = models.TextField()
    due_date = models.DateField(db_index=True)
    status = models.CharField(
        max_length=3, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    completion_report = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.letter.tracking_code} → {self.assigned_to.get_full_name()}"
