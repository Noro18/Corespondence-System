from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser
from apps.inbound_letters.models import Sender, InboundLetter
from django.core.files.uploadedfile import SimpleUploadedFile


class InboundLetterTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username="secuser", password="password123", role=CustomUser.Role.SEKRETARIADU
        )
        self.sender = Sender.objects.create(name="Test Sender", institution="Test Inst")
        self.client.login(username="secuser", password="password123")
        
        self.pdf_content = b"%PDF-1.4 dummy pdf content for testing inline preview and thumbnail"
        self.pdf_file = SimpleUploadedFile("test_letter.pdf", self.pdf_content, content_type="application/pdf")

    def test_creation_and_thumbnail(self):
        letter = InboundLetter.objects.create(
            tracking_code="IN-TEST001",
            title="Test Inbound Letter",
            sender=self.sender,
            letter_date="2026-07-30",
            pdf_file=self.pdf_file,
            registered_by=self.user
        )
        self.assertTrue(bool(letter.thumbnail))
        self.assertIn("thumb_", letter.thumbnail.name)

    def test_detail_and_list_views(self):
        letter = InboundLetter.objects.create(
            tracking_code="IN-TEST002",
            title="Another Test Letter",
            sender=self.sender,
            letter_date="2026-07-30",
            pdf_file=self.pdf_file,
            registered_by=self.user
        )
        response_list = self.client.get(reverse("inbound_letters:list"))
        self.assertEqual(response_list.status_code, 200)
        self.assertContains(response_list, letter.tracking_code)

        response_detail = self.client.get(reverse("inbound_letters:detail", args=[letter.pk]))
        self.assertEqual(response_detail.status_code, 200)
        self.assertContains(response_detail, letter.tracking_code)
        self.assertContains(response_detail, "<iframe")
