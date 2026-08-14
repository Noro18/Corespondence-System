from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.common.choices import LetterCategory
from apps.common.mixins import AdminMixin, PrezidenteMixin, SekretariaduMixin, StaffOrSekretariaduMixin
from apps.common.utils import export_csv_response

from .models import ApprovalStage, OutboundLetter


class OutboundLetterListView(LoginRequiredMixin, ListView):
    model = OutboundLetter
    template_name = "outbound_letters/letter_list.html"
    context_object_name = "letters"
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = LetterCategory.choices
        return context

    def get_queryset(self):
        qs = OutboundLetter.objects.select_related("created_by")
        user = self.request.user
        if user.role not in [user.Role.ADMIN, user.Role.PREZIDENTE]:
            qs = qs.filter(created_by=user)
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs


class OutboundLetterExportCSVView(LoginRequiredMixin, ListView):
    model = OutboundLetter

    def get_queryset(self):
        qs = OutboundLetter.objects.select_related("created_by")
        user = self.request.user
        if user.role not in [user.Role.ADMIN, user.Role.PREZIDENTE]:
            qs = qs.filter(created_by=user)
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        headers = [
            "Tracking Code", "Original Ref No", "Subject", "Recipient Institution",
            "Recipient Name", "Category", "Letter Date", "Created By", "Status"
        ]
        rows = []
        for l in queryset:
            rows.append([
                l.tracking_code,
                l.original_ref_no,
                l.subject,
                l.recipient_institution,
                l.recipient_name,
                l.get_category_display(),
                l.letter_date,
                l.created_by.get_full_name() if l.created_by else "",
                l.get_status_display(),
            ])
        return export_csv_response("outbound_letters.csv", headers, rows)


class OutboundLetterCreateView(StaffOrSekretariaduMixin, LoginRequiredMixin, CreateView):
    model = OutboundLetter
    template_name = "outbound_letters/letter_form.html"
    fields = [
        "subject", "recipient_name", "recipient_institution",
        "recipient_address", "original_ref_no", "letter_date",
        "pdf_file", "notes", "category",
    ]
    extra_context = {"title": "Create Outbound Letter"}
    success_url = reverse_lazy("outbound_letters:list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["letter_date"].widget = forms.DateInput(
            attrs={"type": "date", "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#900000]"}
        )
        for field in form.fields.values():
            field.widget.attrs.setdefault("class",
                "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#900000]"
            )
            if field.required:
                field.widget.attrs["required"] = "required"
        return form


class OutboundLetterUpdateView(StaffOrSekretariaduMixin, LoginRequiredMixin, UpdateView):
    model = OutboundLetter
    template_name = "outbound_letters/letter_form.html"
    fields = [
        "subject", "recipient_name", "recipient_institution",
        "recipient_address", "original_ref_no", "letter_date",
        "pdf_file", "notes", "category",
    ]
    extra_context = {"title": "Edit Rejected Outbound Letter"}

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        # Only allow editing if status is Rejected (REJ)
        qs = qs.filter(status=OutboundLetter.Status.REJECTED)
        if user.role not in [user.Role.ADMIN, user.Role.PREZIDENTE]:
            qs = qs.filter(created_by=user)
        return qs

    def form_valid(self, form):
        # Reset status back to Draft (or keep as Draft so it can be reviewed again)
        form.instance.status = OutboundLetter.Status.DRAFT
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("outbound_letters:detail", kwargs={"pk": self.object.pk})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["letter_date"].widget = forms.DateInput(
            attrs={"type": "date", "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#900000]"}
        )
        for field in form.fields.values():
            field.widget.attrs.setdefault("class",
                "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#900000]"
            )
            if field.required:
                field.widget.attrs["required"] = "required"
        return form


class OutboundLetterDetailView(LoginRequiredMixin, DetailView):
    model = OutboundLetter
    template_name = "outbound_letters/letter_detail.html"
    context_object_name = "letter"

    def get_queryset(self):
        qs = OutboundLetter.objects.select_related("created_by").prefetch_related("approval_stages__reviewer")
        user = self.request.user
        if user.role in [user.Role.ADMIN, user.Role.PREZIDENTE]:
            return qs
        return qs.filter(created_by=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_review"] = self.request.user.role in [
            self.request.user.Role.ADMIN, self.request.user.Role.PREZIDENTE
        ]
        context["can_dispatch"] = self.request.user.role in [
            self.request.user.Role.ADMIN, self.request.user.Role.PREZIDENTE
        ]
        return context


class OutboundLetterReviewView(PrezidenteMixin, LoginRequiredMixin, UpdateView):
    model = OutboundLetter
    template_name = "outbound_letters/letter_review.html"
    context_object_name = "letter"
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stage"] = self.kwargs.get("stage", "REV")
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        decision = request.POST.get("decision")
        comments = request.POST.get("comments", "")
        stage_code = self.kwargs.get("stage", "REV")

        if decision == "APR":
            self.object.status = OutboundLetter.Status.APPROVED
        elif decision == "REJ":
            self.object.status = OutboundLetter.Status.REJECTED

        self.object.save()

        ApprovalStage.objects.create(
            letter=self.object,
            stage=stage_code,
            decision=decision,
            reviewer=request.user,
            comments=comments,
            decided_at=timezone.now(),
        )

        return HttpResponseRedirect(
            reverse("outbound_letters:detail", kwargs={"pk": self.object.pk})
        )


class OutboundLetterDispatchView(PrezidenteMixin, LoginRequiredMixin, UpdateView):
    model = OutboundLetter
    fields = []

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status = OutboundLetter.Status.DISPATCHED
        self.object.save()

        ApprovalStage.objects.create(
            letter=self.object,
            stage=ApprovalStage.Stage.DISPATCH,
            decision=ApprovalStage.Decision.APPROVED,
            reviewer=request.user,
            decided_at=timezone.now(),
        )

        return HttpResponseRedirect(
            reverse("outbound_letters:detail", kwargs={"pk": self.object.pk})
        )


class OutboundLetterDeleteView(AdminMixin, LoginRequiredMixin, DeleteView):
    model = OutboundLetter
    template_name = "outbound_letters/letter_confirm_delete.html"
    success_url = reverse_lazy("outbound_letters:list")
