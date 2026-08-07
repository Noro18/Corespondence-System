from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser
from apps.inbound_letters.models import Assignment, Sender, InboundLetter
from django.core.files.uploadedfile import SimpleUploadedFile


# Create your tests here.
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


class AssignmentWorkflowTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = Sender.objects.create(name="Test Sender")
        self.admin = CustomUser.objects.create_user(
            username="admin", password="password123", role=CustomUser.Role.ADMIN
        )
        self.prez = CustomUser.objects.create_user(
            username="prez", password="password123", role=CustomUser.Role.PREZIDENTE
        )
        self.sek = CustomUser.objects.create_user(
            username="sek", password="password123", role=CustomUser.Role.SEKRETARIADU
        )
        self.staff = CustomUser.objects.create_user(
            username="staff1", password="password123", role=CustomUser.Role.STAFF
        )
        self.staff2 = CustomUser.objects.create_user(
            username="staff2", password="password123", role=CustomUser.Role.STAFF
        )
        self.letter = InboundLetter.objects.create(
            tracking_code="IN-WORK001",
            title="Workflow Test Letter",
            sender=self.sender,
            letter_date="2026-07-30",
            registered_by=self.sek,
        )
        self.assign_url = reverse("inbound_letters:assign", args=[self.letter.pk])

    def create_assignment(self, letter=None, staff=None, status=Assignment.Status.PENDING):
        return Assignment.objects.create(
            letter=letter or self.letter,
            assigned_by=self.prez,
            assigned_to=staff or self.staff,
            instructions="Handle this",
            due_date="2026-08-15",
            status=status,
        )

    def test_despaxu_blocked_for_sekretariadu(self):
        self.client.login(username="sek", password="password123")
        response = self.client.post(self.assign_url, {
            "assigned_to": self.staff.pk,
            "instructions": "Handle this",
            "due_date": "2026-08-15",
        })
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(Assignment.objects.exists())

    def test_despaxu_creates_assignment_and_marks_letter_assigned(self):
        self.client.login(username="prez", password="password123")
        response = self.client.post(self.assign_url, {
            "assigned_to": self.staff.pk,
            "instructions": "Handle this",
            "due_date": "2026-08-15",
        })
        self.assertEqual(response.status_code, 302)
        assignment = Assignment.objects.get()
        self.assertEqual(assignment.letter, self.letter)
        self.assertEqual(assignment.assigned_by, self.prez)
        self.assertEqual(assignment.assigned_to, self.staff)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.status, InboundLetter.Status.ASSIGNED)

    def test_despaxu_form_only_lists_staff_users(self):
        self.client.login(username="prez", password="password123")
        response = self.client.get(self.assign_url)
        form = response.context["form"]
        self.assertNotIn(self.prez, form.fields["assigned_to"].queryset)
        self.assertIn(self.staff, form.fields["assigned_to"].queryset)

    def test_staff_cannot_update_another_staff_assignment(self):
        assignment = self.create_assignment(staff=self.staff)
        url = reverse("inbound_letters:assignment_update", args=[assignment.pk])
        self.client.login(username="staff2", password="password123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_can_update_own_assignment(self):
        assignment = self.create_assignment(staff=self.staff)
        url = reverse("inbound_letters:assignment_update", args=[assignment.pk])
        self.client.login(username="staff1", password="password123")
        response = self.client.post(url, {
            "status": Assignment.Status.COMPLETED,
            "completion_report": "Done",
        })
        self.assertEqual(response.status_code, 302)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, Assignment.Status.COMPLETED)
        self.assertIsNotNone(assignment.completed_at)

    def test_letter_completed_when_all_assignments_done(self):
        a1 = self.create_assignment(staff=self.staff)
        a2 = self.create_assignment(staff=self.staff2)
        a1.status = Assignment.Status.COMPLETED
        a1.save()
        url = reverse("inbound_letters:assignment_update", args=[a2.pk])
        self.client.login(username="staff2", password="password123")
        self.client.post(url, {
            "status": Assignment.Status.COMPLETED,
            "completion_report": "Done too",
        })
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.status, InboundLetter.Status.COMPLETED)

    def test_letter_stays_assigned_when_not_all_done(self):
        a1 = self.create_assignment(staff=self.staff)
        a2 = self.create_assignment(staff=self.staff2)
        url = reverse("inbound_letters:assignment_update", args=[a1.pk])
        self.client.login(username="staff1", password="password123")
        self.client.post(url, {
            "status": Assignment.Status.COMPLETED,
            "completion_report": "Done",
        })
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.status, InboundLetter.Status.ASSIGNED)

