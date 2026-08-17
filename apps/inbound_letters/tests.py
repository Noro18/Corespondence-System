from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser
from apps.common.choices import LetterCategory
from apps.inbound_letters.models import Assignment, InboundDecision, Sender, InboundLetter
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

    def test_despaxu_blocked_before_acceptance(self):
        self.client.login(username="prez", password="password123")
        response = self.client.get(self.assign_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("inbound_letters:detail", args=[self.letter.pk])
        )
        self.assertFalse(Assignment.objects.exists())

    def test_despaxu_creates_assignment_and_marks_letter_assigned(self):
        self.letter.status = InboundLetter.Status.ACCEPTED
        self.letter.save()
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
        self.letter.status = InboundLetter.Status.ACCEPTED
        self.letter.save()
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


class CategoryTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = Sender.objects.create(name="Test Sender")
        self.sek = CustomUser.objects.create_user(
            username="sek", password="password123", role=CustomUser.Role.SEKRETARIADU
        )
        self.prez = CustomUser.objects.create_user(
            username="prez", password="password123", role=CustomUser.Role.PREZIDENTE
        )
        self.letter = InboundLetter.objects.create(
            tracking_code="IN-CAT001",
            title="Action Letter",
            sender=self.sender,
            letter_date="2026-07-30",
            registered_by=self.sek,
            category=LetterCategory.PEDIDU,
        )
        self.client.login(username="sek", password="password123")

    def test_create_form_includes_category(self):
        response = self.client.get(reverse("inbound_letters:create"))
        self.assertContains(response, 'name="category"')

    def test_default_category_is_pedidu(self):
        letter = InboundLetter.objects.create(
            tracking_code="IN-CAT002",
            title="No Category Given",
            sender=self.sender,
            letter_date="2026-07-30",
            registered_by=self.sek,
        )
        self.assertEqual(letter.category, LetterCategory.PEDIDU)

    def test_list_filter_by_category(self):
        InboundLetter.objects.create(
            tracking_code="IN-CAT003",
            title="Invitation Letter",
            sender=self.sender,
            letter_date="2026-07-30",
            registered_by=self.sek,
            category=LetterCategory.CONVITE,
        )
        response = self.client.get(reverse("inbound_letters:list"), {"category": LetterCategory.CONVITE})
        self.assertContains(response, "IN-CAT003")
        self.assertNotContains(response, "IN-CAT001")

    def test_detail_shows_category_badge(self):
        response = self.client.get(reverse("inbound_letters:detail", args=[self.letter.pk]))
        self.assertContains(response, self.letter.get_category_display())

    def test_despaxu_blocked_for_konvite_letter(self):
        self.letter.category = LetterCategory.CONVITE
        self.letter.status = InboundLetter.Status.ACCEPTED
        self.letter.save()
        self.client.login(username="prez", password="password123")
        response = self.client.get(reverse("inbound_letters:assign", args=[self.letter.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("inbound_letters:detail", args=[self.letter.pk]))

    def test_despaxu_allowed_for_pedidu_after_acceptance(self):
        self.letter.status = InboundLetter.Status.ACCEPTED
        self.letter.save()
        self.client.login(username="prez", password="password123")
        response = self.client.get(reverse("inbound_letters:assign", args=[self.letter.pk]))
        self.assertEqual(response.status_code, 200)


class ArchiveTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = Sender.objects.create(name="Test Sender")
        self.sek = CustomUser.objects.create_user(
            username="sek", password="password123", role=CustomUser.Role.SEKRETARIADU
        )
        self.prez = CustomUser.objects.create_user(
            username="prez", password="password123", role=CustomUser.Role.PREZIDENTE
        )
        self.admin = CustomUser.objects.create_user(
            username="admin", password="password123", role=CustomUser.Role.ADMIN
        )
        self.staff = CustomUser.objects.create_user(
            username="staff", password="password123", role=CustomUser.Role.STAFF
        )
        self.letter = InboundLetter.objects.create(
            tracking_code="IN-ARC001",
            title="Invitation",
            sender=self.sender,
            letter_date="2026-07-30",
            registered_by=self.sek,
            category=LetterCategory.CONVITE,
        )

    def archive_url(self):
        return reverse("inbound_letters:archive", args=[self.letter.pk])

    def test_prez_archives_informational_letter(self):
        self.client.login(username="prez", password="password123")
        response = self.client.post(self.archive_url())
        self.assertEqual(response.status_code, 302)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.status, InboundLetter.Status.ARCHIVED)

    def test_admin_archives_completed_pedidu_letter(self):
        self.letter.category = LetterCategory.PEDIDU
        self.letter.status = InboundLetter.Status.COMPLETED
        self.letter.save()
        self.client.login(username="admin", password="password123")
        response = self.client.post(self.archive_url())
        self.assertEqual(response.status_code, 302)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.status, InboundLetter.Status.ARCHIVED)

    def test_sekretariadu_cannot_archive(self):
        self.client.login(username="sek", password="password123")
        response = self.client.post(self.archive_url())
        self.assertNotEqual(response.status_code, 200)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.status, InboundLetter.Status.REGISTERED)

    def test_konvite_detail_has_archive_not_despaxu(self):
        self.client.login(username="prez", password="password123")
        response = self.client.get(reverse("inbound_letters:detail", args=[self.letter.pk]))
        self.assertContains(response, "Archive")
        self.assertNotContains(response, "Despaxu")

    def test_accepted_pedidu_detail_has_despaxu_not_archive(self):
        self.letter.category = LetterCategory.PEDIDU
        self.letter.status = InboundLetter.Status.ACCEPTED
        self.letter.save()
        self.client.login(username="prez", password="password123")
        response = self.client.get(reverse("inbound_letters:detail", args=[self.letter.pk]))
        self.assertContains(response, "Despaxu")
        self.assertNotContains(response, ">Archive</button>")

    def test_completed_pedidu_detail_has_archive(self):
        self.letter.category = LetterCategory.PEDIDU
        self.letter.status = InboundLetter.Status.COMPLETED
        self.letter.save()
        self.client.login(username="prez", password="password123")
        response = self.client.get(reverse("inbound_letters:detail", args=[self.letter.pk]))
        self.assertContains(response, "Archive")
        self.assertNotContains(response, "Despaxu")

    def test_archived_letter_has_no_archive_or_despaxu_button(self):
        self.letter.status = InboundLetter.Status.ARCHIVED
        self.letter.save()
        self.client.login(username="prez", password="password123")
        response = self.client.get(reverse("inbound_letters:detail", args=[self.letter.pk]))
        self.assertNotContains(response, ">Archive</button>")
        self.assertNotContains(response, ">Despaxu</a>")

    def test_staff_has_no_archive_button(self):
        Assignment.objects.create(
            letter=self.letter,
            assigned_by=self.prez,
            assigned_to=self.staff,
            instructions="Handle this",
            due_date="2026-08-15",
        )
        self.client.login(username="staff", password="password123")
        response = self.client.get(reverse("inbound_letters:detail", args=[self.letter.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, ">Archive</button>")

    def test_csv_export_rbac(self):
        # Create a second letter not assigned to staff
        InboundLetter.objects.create(
            tracking_code="IN-OTHER01",
            title="Other Letter",
            sender=self.sender,
            letter_date="2026-07-30",
            registered_by=self.sek,
        )
        # Assign self.letter to staff
        Assignment.objects.create(
            letter=self.letter,
            assigned_by=self.prez,
            assigned_to=self.staff,
            instructions="Test assignment",
            due_date="2026-08-15",
        )
        # Staff export should only contain their assigned letter (IN-ARC001)
        self.client.login(username="staff", password="password123")
        res = self.client.get(reverse("inbound_letters:export"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn(b"IN-ARC001", res.content)
        self.assertNotIn(b"IN-OTHER01", res.content)

        # Admin export should contain both
        self.client.login(username="admin", password="password123")
        res_admin = self.client.get(reverse("inbound_letters:export"))
        self.assertEqual(res_admin.status_code, 200)
        self.assertIn(b"IN-ARC001", res_admin.content)
        self.assertIn(b"IN-OTHER01", res_admin.content)


class InboundLetterEditTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = Sender.objects.create(name="Test Sender")
        self.sek = CustomUser.objects.create_user(
            username="sek", password="password123", role=CustomUser.Role.SEKRETARIADU
        )
        self.sek2 = CustomUser.objects.create_user(
            username="sek2", password="password123", role=CustomUser.Role.SEKRETARIADU
        )
        self.admin = CustomUser.objects.create_user(
            username="admin", password="password123", role=CustomUser.Role.ADMIN
        )
        self.staff = CustomUser.objects.create_user(
            username="staff", password="password123", role=CustomUser.Role.STAFF
        )
        self.pdf = SimpleUploadedFile("edit_letter.pdf", b"%PDF-1.4 dummy", content_type="application/pdf")
        self.letter = InboundLetter.objects.create(
            tracking_code="IN-EDIT001",
            title="Original Title",
            original_ref_no="REF-001",
            sender=self.sender,
            letter_date="2026-07-30",
            pdf_file=self.pdf,
            registered_by=self.sek,
        )
        self.url = reverse("inbound_letters:edit", args=[self.letter.pk])

    def post_data(self):
        return {
            "title": "Updated Title",
            "original_ref_no": "REF-002",
            "sender_name": "New Sender",
            "letter_date": "2026-08-01",
            "category": LetterCategory.PEDIDU,
            "pdf_file": SimpleUploadedFile("edit_letter.pdf", b"%PDF-1.4 dummy", content_type="application/pdf"),
        }

    def test_creator_sek_can_edit_own_letter(self):
        self.client.login(username="sek", password="password123")
        response = self.client.post(self.url, self.post_data())
        self.assertEqual(response.status_code, 302)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.title, "Updated Title")
        self.assertEqual(self.letter.original_ref_no, "REF-002")
        self.assertEqual(self.letter.sender.name, "New Sender")

    def test_edit_without_new_pdf_keeps_existing_file(self):
        data = self.post_data()
        data.pop("pdf_file")
        original_pdf = self.letter.pdf_file.name
        self.client.login(username="sek", password="password123")
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.title, "Updated Title")
        self.assertEqual(self.letter.pdf_file.name, original_pdf)

    def test_creator_sek_can_get_edit_form_with_sender_prefilled(self):
        self.client.login(username="sek", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Test Sender"')
        self.assertContains(response, "Edit Inbound Letter")

    def test_sek_cannot_edit_others_letter(self):
        self.client.login(username="sek2", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_creator_sek_cannot_edit_completed_letter(self):
        self.letter.status = InboundLetter.Status.COMPLETED
        self.letter.save()
        self.client.login(username="sek", password="password123")
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_creator_sek_cannot_edit_archived_letter(self):
        self.letter.status = InboundLetter.Status.ARCHIVED
        self.letter.save()
        self.client.login(username="sek", password="password123")
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_admin_can_edit_any_status_letter(self):
        self.letter.status = InboundLetter.Status.COMPLETED
        self.letter.save()
        self.client.login(username="admin", password="password123")
        response = self.client.post(self.url, self.post_data())
        self.assertEqual(response.status_code, 302)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.title, "Updated Title")
        self.assertEqual(self.letter.status, InboundLetter.Status.COMPLETED)

    def test_staff_cannot_edit_letter(self):
        self.client.login(username="staff", password="password123")
        self.assertEqual(self.client.get(self.url).status_code, 403)


class InboundLetterDecisionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = Sender.objects.create(name="Test Sender")
        self.prez = CustomUser.objects.create_user(
            username="prez", password="password123", role=CustomUser.Role.PREZIDENTE
        )
        self.sek = CustomUser.objects.create_user(
            username="sek", password="password123", role=CustomUser.Role.SEKRETARIADU
        )
        self.letter = InboundLetter.objects.create(
            tracking_code="IN-DEC001",
            title="Decision Letter",
            sender=self.sender,
            letter_date="2026-07-30",
            registered_by=self.sek,
            category=LetterCategory.CONVITE,
        )
        self.decide_url = reverse("inbound_letters:decide", args=[self.letter.pk])

    def test_prez_accepts_letter(self):
        self.client.login(username="prez", password="password123")
        response = self.client.post(self.decide_url, {
            "decision": InboundDecision.Decision.ACCEPTED,
            "comments": "Accepted for archive",
        })
        self.assertEqual(response.status_code, 302)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.status, InboundLetter.Status.ACCEPTED)
        decision = InboundDecision.objects.get()
        self.assertEqual(decision.decision, InboundDecision.Decision.ACCEPTED)
        self.assertEqual(decision.decided_by, self.prez)
        self.assertEqual(decision.comments, "Accepted for archive")
        self.assertIsNotNone(decision.decided_at)

    def test_prez_rejects_letter(self):
        self.client.login(username="prez", password="password123")
        response = self.client.post(self.decide_url, {
            "decision": InboundDecision.Decision.REJECTED,
        })
        self.assertEqual(response.status_code, 302)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.status, InboundLetter.Status.REJECTED)
        self.assertEqual(
            InboundDecision.objects.get().decision, InboundDecision.Decision.REJECTED
        )

    def test_rejected_letter_can_be_reopened_and_accepted(self):
        self.client.login(username="prez", password="password123")
        self.client.post(self.decide_url, {"decision": InboundDecision.Decision.REJECTED})
        response = self.client.post(self.decide_url, {
            "decision": InboundDecision.Decision.ACCEPTED,
        })
        self.assertEqual(response.status_code, 302)
        self.letter.refresh_from_db()
        self.assertEqual(self.letter.status, InboundLetter.Status.ACCEPTED)
        self.assertEqual(InboundDecision.objects.count(), 2)

    def test_sekretariadu_cannot_decide(self):
        self.client.login(username="sek", password="password123")
        response = self.client.post(self.decide_url, {
            "decision": InboundDecision.Decision.ACCEPTED,
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(InboundDecision.objects.exists())

    def test_decide_blocked_for_archived_letter(self):
        self.letter.status = InboundLetter.Status.ARCHIVED
        self.letter.save()
        self.client.login(username="prez", password="password123")
        response = self.client.post(self.decide_url, {
            "decision": InboundDecision.Decision.ACCEPTED,
        })
        self.assertEqual(response.status_code, 404)

    def test_accepted_letter_cannot_be_decided_again(self):
        self.letter.status = InboundLetter.Status.ACCEPTED
        self.letter.save()
        self.client.login(username="prez", password="password123")
        response = self.client.post(self.decide_url, {
            "decision": InboundDecision.Decision.ACCEPTED,
        })
        self.assertEqual(response.status_code, 404)


