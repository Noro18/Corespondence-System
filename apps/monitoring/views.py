from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from apps.inbound_letters.models import Assignment, InboundLetter


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "monitoring/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        if user.role in [user.Role.ADMIN, user.Role.PREZIDENTE]:
            letters = InboundLetter.objects.all()
            assignments = Assignment.objects.all()
        elif user.role == user.Role.SEKRETARIADU:
            letters = InboundLetter.objects.filter(registered_by=user)
            assignments = Assignment.objects.filter(letter__registered_by=user)
        else:
            letters = InboundLetter.objects.filter(assignments__assigned_to=user)
            assignments = Assignment.objects.filter(assigned_to=user)

        context["total_pending"] = letters.filter(status="REG").count()
        context["in_progress"] = assignments.filter(status="IPR").count()
        context["overdue"] = assignments.filter(
            status__in=["PND", "IPR"], due_date__lt=today
        ).count()
        context["recent_letters"] = letters.select_related("sender")[:10]
        context["my_tasks"] = assignments.filter(assigned_to=user).select_related(
            "letter"
        )[:10]
        context["overdue_assignments"] = assignments.filter(
            status__in=["PND", "IPR"], due_date__lt=today
        ).select_related("letter", "assigned_to")[:10]

        return context
