from django.test import TestCase

from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser


class AdministratorWorkerRoleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_user(
            username="adminuser", password="password123", role=CustomUser.Role.ADMIN
        )
        self.admw_user = CustomUser.objects.create_user(
            username="admwuser", password="password123", role=CustomUser.Role.ADMIN_WORKER
        )
        self.staff_user = CustomUser.objects.create_user(
            username="staffuser", password="password123", role=CustomUser.Role.STAFF
        )

    def test_admw_cannot_list_users(self):
        self.client.login(username="admwuser", password="password123")
        response = self.client.get(reverse("accounts:user_list"))
        self.assertEqual(response.status_code, 403)

    def test_staff_cannot_list_users(self):
        self.client.login(username="staffuser", password="password123")
        response = self.client.get(reverse("accounts:user_list"))
        self.assertNotEqual(response.status_code, 200)

    def test_admw_cannot_delete_user(self):
        self.client.login(username="admwuser", password="password123")
        response = self.client.post(reverse("accounts:user_delete", args=[self.staff_user.pk]))
        # ADMW should be forbidden (403) from deleting users
        self.assertEqual(response.status_code, 403)

    def test_sek_cannot_register_inbound_letter(self):
        sek_user = CustomUser.objects.create_user(
            username="sekuser", password="password123", role=CustomUser.Role.SEKRETARIADU
        )
        self.client.login(username="sekuser", password="password123")
        response = self.client.get(reverse("inbound_letters:create"))
        self.assertEqual(response.status_code, 403)

    def test_admw_can_register_inbound_letter(self):
        self.client.login(username="admwuser", password="password123")
        response = self.client.get(reverse("inbound_letters:create"))
        self.assertEqual(response.status_code, 200)

