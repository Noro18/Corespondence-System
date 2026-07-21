from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic import TemplateView

from apps.inbound_letters.models import Assignment, InboundLetter


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "monitoring/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        today = timezone.now().date()

        context["total_pending"] = InboundLetter.objects.filter(status="REG").count()
        context["in_progress"] = Assignment.objects.filter(status="IPR").count()
        context["overdue"] = (
            Assignment.objects.filter(status__in=["PND", "IPR"], due_date__lt=today).count()
        )

        context["recent_letters"] = InboundLetter.objects.select_related(
            "sender", "registered_by"
        )[:10]

        context["my_tasks"] = Assignment.objects.filter(
            assigned_to=user
        ).select_related("letter", "assigned_by")[:10]

        context["overdue_assignments"] = (
            Assignment.objects.filter(status__in=["PND", "IPR"], due_date__lt=today)
            .select_related("letter", "assigned_to", "assigned_by")[:10]
        )

        return context
