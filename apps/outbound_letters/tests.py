from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from apps.accounts.models import CustomUser

from .models import OutboundLetter


class OutboundLetterEditTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = CustomUser.objects.create_user(
            username="staff1", password="password123", role=CustomUser.Role.STAFF
        )
        self.staff2 = CustomUser.objects.create_user(
            username="staff2", password="password123", role=CustomUser.Role.STAFF
        )
        self.admin = CustomUser.objects.create_user(
            username="admin", password="password123", role=CustomUser.Role.ADMIN
        )
        self.prez = CustomUser.objects.create_user(
            username="prez", password="password123", role=CustomUser.Role.PREZIDENTE
        )
        self.pdf = SimpleUploadedFile("edit_out.pdf", b"%PDF-1.4 dummy", content_type="application/pdf")
        self.letter = OutboundLetter.objects.create(
            tracking_code="OUT-EDIT001",
            subject="Original Subject",
            recipient_name="Recipient",
            recipient_institution="Institution",
            recipient_address="Address",
            original_ref_no="REF-001",
            letter_date="2026-07-30",
            pdf_file=self.pdf,
            created_by=self.staff,
        )
        self.url = reverse("outbound_letters:edit", args=[self.letter.pk])

    def post_data(self):
        return {
            "subject": "Updated Subject",
            "recipient_name": "Recipient",
            "recipient_institution": "Institution",
            "recipient_address": "Address",
            "original_ref_no": "REF-002",
            "letter_date": "2026-08-01",
            "category": "PED",
            "pdf_file": SimpleUploadedFile("edit_out.pdf", b"%PDF-1.4 dummy", content_type="application/pdf"),
        }

    def test_creator_staff_can_edit_own_draft(self):
        self.client.login(username="staff1", password="password123")
        response = self.client.post(self.url, self.post_data())
        self.assertEqual(response.status_code, 302)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.subject, "Updated Subject")
        self.assertEqual(self.letter.status, OutboundLetter.Status.DRAFT)

    def test_edit_without_new_pdf_keeps_existing_file(self):
        data = self.post_data()
        data.pop("pdf_file")
        original_pdf = self.letter.pdf_file.name
        self.client.login(username="staff1", password="password123")
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.subject, "Updated Subject")
        self.assertEqual(self.letter.pdf_file.name, original_pdf)

    def test_creator_staff_can_edit_rejected_letter_and_resets_to_draft(self):
        self.letter.status = OutboundLetter.Status.REJECTED
        self.letter.save()
        self.client.login(username="staff1", password="password123")
        response = self.client.post(self.url, self.post_data())
        self.assertEqual(response.status_code, 302)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.status, OutboundLetter.Status.DRAFT)

    def test_creator_staff_cannot_edit_review_letter(self):
        self.letter.status = OutboundLetter.Status.IN_REVIEW
        self.letter.save()
        self.client.login(username="staff1", password="password123")
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_creator_staff_cannot_edit_approved_letter(self):
        self.letter.status = OutboundLetter.Status.APPROVED
        self.letter.save()
        self.client.login(username="staff1", password="password123")
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_creator_staff_cannot_edit_dispatched_letter(self):
        self.letter.status = OutboundLetter.Status.DISPATCHED
        self.letter.save()
        self.client.login(username="staff1", password="password123")
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_staff_cannot_edit_others_letter(self):
        self.client.login(username="staff2", password="password123")
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_admin_can_edit_any_status_letter(self):
        self.letter.status = OutboundLetter.Status.DISPATCHED
        self.letter.save()
        self.client.login(username="admin", password="password123")
        response = self.client.post(self.url, self.post_data())
        self.assertEqual(response.status_code, 302)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.subject, "Updated Subject")
        self.assertEqual(self.letter.status, OutboundLetter.Status.DISPATCHED)

    def test_prezidente_cannot_edit_letter(self):
        self.client.login(username="prez", password="password123")
        self.assertEqual(self.client.get(self.url).status_code, 403)
