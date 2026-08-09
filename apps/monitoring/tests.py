from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardChartTests(TestCase):
    def setUp(self):
        self.prez_user = User.objects.create_user(
            username="prez", password="password", role=User.Role.PREZIDENTE, first_name="Prez", last_name="User"
        )
        self.client = Client()

    def test_dashboard_view_contains_charts_context(self):
        self.client.login(username="prez", password="password")
        response = self.client.get(reverse("monitoring:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("chart_inbound_labels", response.context)
        self.assertIn("chart_inbound_values", response.context)
        self.assertIn("chart_outbound_labels", response.context)
        self.assertIn("chart_outbound_values", response.context)
        self.assertIn("chart_monthly_labels", response.context)
        self.assertIn("chart_monthly_values", response.context)
        self.assertIn("chart_tasks_labels", response.context)
        self.assertIn("chart_tasks_values", response.context)

