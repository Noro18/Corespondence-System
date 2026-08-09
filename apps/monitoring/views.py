from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView
from django.db.models import Count
from django.db.models.functions import TruncMonth

from apps.common.choices import LetterCategory
from apps.inbound_letters.models import Assignment, InboundLetter
from apps.outbound_letters.models import OutboundLetter


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "monitoring/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        if user.role in [user.Role.ADMIN, user.Role.PREZIDENTE, user.Role.SEKRETARIADU]:
            letters = InboundLetter.objects.all()
            assignments = Assignment.objects.all()
            outbound_letters = OutboundLetter.objects.all()
        else:
            letters = InboundLetter.objects.filter(assignments__assigned_to=user).distinct()
            assignments = Assignment.objects.filter(assigned_to=user)
            outbound_letters = OutboundLetter.objects.filter(created_by=user)

        context["total_letters"] = letters.count()
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
        context["category_counts"] = {
            category: letters.filter(category=category).count()
            for category, _ in LetterCategory.choices
        }

        # Chart datasets
        # 1. Inbound status counts
        inbound_status_map = dict(InboundLetter.Status.choices)
        inbound_status_data = {
            code: letters.filter(status=code).count()
            for code, _ in InboundLetter.Status.choices
        }
        context["chart_inbound_labels"] = [label for label in inbound_status_map.values()]
        context["chart_inbound_values"] = [inbound_status_data[code] for code in inbound_status_map.keys()]

        # 2. Outbound status counts
        outbound_status_map = dict(OutboundLetter.Status.choices)
        outbound_status_data = {
            code: outbound_letters.filter(status=code).count()
            for code, _ in OutboundLetter.Status.choices
        }
        context["chart_outbound_labels"] = [label for label in outbound_status_map.values()]
        context["chart_outbound_values"] = [outbound_status_data[code] for code in outbound_status_map.keys()]

        # 3. Letters per month (last 6 months)
        six_months_ago = today - timezone.timedelta(days=180)
        monthly_qs = (
            letters.filter(received_date__gte=six_months_ago)
            .annotate(month=TruncMonth("received_date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        monthly_dict = {item["month"].strftime("%b %Y"): item["count"] for item in monthly_qs if item["month"]}
        
        # Build list for last 6 months to ensure chronological continuity
        monthly_labels = []
        monthly_values = []
        for i in range(5, -1, -1):
            # approximate month navigation
            target_date = today - timezone.timedelta(days=i*30)
            m_key = target_date.strftime("%b %Y")
            monthly_labels.append(m_key)
            monthly_values.append(monthly_dict.get(m_key, 0))
        
        context["chart_monthly_labels"] = monthly_labels
        context["chart_monthly_values"] = monthly_values

        # 4. Tasks overview by status
        task_status_map = dict(Assignment.Status.choices)
        task_status_data = {
            code: assignments.filter(status=code).count()
            for code, _ in Assignment.Status.choices
        }
        context["chart_tasks_labels"] = [label for label in task_status_map.values()]
        context["chart_tasks_values"] = [task_status_data[code] for code in task_status_map.keys()]

        return context
