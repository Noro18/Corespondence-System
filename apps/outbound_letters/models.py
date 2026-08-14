import datetime

from django.conf import settings
from django.db import models

from apps.common.choices import LetterCategory


class OutboundLetter(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRF", "Draft"
        IN_REVIEW = "REV", "In Review"
        APPROVED = "APR", "Approved"
        REJECTED = "REJ", "Rejected"
        DISPATCHED = "DSP", "Dispatched"

    tracking_code = models.CharField(max_length=30, unique=True, editable=False)
    subject = models.CharField(max_length=255)
    recipient_name = models.CharField(max_length=255)
    recipient_institution = models.CharField(max_length=255)
    recipient_address = models.TextField()
    original_ref_no = models.CharField(max_length=100)
    letter_date = models.DateField()
    pdf_file = models.FileField(upload_to="outbound_pdfs/")
    thumbnail = models.ImageField(upload_to="outbound_thumbnails/", blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="outbound_letters",
    )
    status = models.CharField(
        max_length=3, choices=Status.choices, default=Status.DRAFT, db_index=True
    )
    category = models.CharField(
        max_length=3, choices=LetterCategory.choices,
        default=LetterCategory.ASSUNTO, db_index=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.tracking_code:
            today = datetime.date.today()
            prefix = f"OUT-{today.strftime('%Y%m%d')}"
            last = (
                OutboundLetter.objects.filter(tracking_code__startswith=prefix)
                .order_by("tracking_code")
                .last()
            )
            next_num = 1
            if last:
                try:
                    next_num = int(last.tracking_code.split("-")[-1]) + 1
                except (ValueError, IndexError):
                    pass
            self.tracking_code = f"{prefix}-{next_num:04d}"
        
        # Check if this is a new instance or if the pdf_file has changed / thumbnail is missing
        old_pdf = None
        if not is_new:
            try:
                old_pdf = OutboundLetter.objects.filter(pk=self.pk).values_list('pdf_file', flat=True).first()
            except Exception:
                pass

        super().save(*args, **kwargs)

        # Generate or regenerate thumbnail if it's new, missing, or pdf_file changed
        has_pdf_changed = old_pdf and old_pdf != self.pdf_file.name
        if (is_new or not self.thumbnail or has_pdf_changed) and self.pdf_file:
            try:
                import fitz
                import os
                from django.core.files.base import ContentFile
                import io

                if hasattr(self.pdf_file, 'seek'):
                    self.pdf_file.seek(0)

                pdf_bytes = self.pdf_file.read()
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                if len(doc) > 0:
                    page = doc[0]
                    pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
                    thumb_io = io.BytesIO(pix.tobytes("png"))
                    thumb_name = f"thumb_out_{self.pk}_{os.path.basename(self.pdf_file.name)}.png"
                    self.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
                    super().save(update_fields=['thumbnail'])
                doc.close()
            except Exception:
                try:
                    from PIL import Image, ImageDraw
                    import os
                    img = Image.new('RGB', (200, 260), color=(240, 242, 245))
                    d = ImageDraw.Draw(img)
                    d.rectangle([(10, 10), (190, 250)], outline=(200, 204, 210), width=2)
                    d.text((20, 30), "PDF DOCUMENT", fill=(30, 41, 59))
                    d.text((20, 60), f"Code: {self.tracking_code[:12]}", fill=(71, 85, 105))
                    
                    thumb_name = f"thumb_out_{self.pk}_{os.path.basename(self.pdf_file.name)}.png"
                    from django.core.files.base import ContentFile
                    import io
                    thumb_io = io.BytesIO()
                    img.save(thumb_io, format='PNG')
                    self.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
                    super().save(update_fields=['thumbnail'])
                except Exception:
                    pass

    def __str__(self):
        return f"{self.tracking_code} - {self.subject}"

    def __str__(self):
        return f"{self.tracking_code} - {self.subject}"


class ApprovalStage(models.Model):
    class Stage(models.TextChoices):
        REVIEW = "REV", "Review"
        APPROVE = "APR", "Approval"
        DISPATCH = "DSP", "Dispatch"

    class Decision(models.TextChoices):
        PENDING = "PND", "Pending"
        APPROVED = "APR", "Approved"
        REJECTED = "REJ", "Rejected"

    letter = models.ForeignKey(
        OutboundLetter, on_delete=models.CASCADE, related_name="approval_stages"
    )
    stage = models.CharField(max_length=3, choices=Stage.choices)
    decision = models.CharField(
        max_length=3, choices=Decision.choices, default=Decision.PENDING
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approval_decisions",
    )
    comments = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.letter.tracking_code} - {self.get_stage_display()} ({self.get_decision_display()})"
