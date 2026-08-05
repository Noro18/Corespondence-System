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

from apps.common.mixins import AdminMixin, PrezidenteMixin, SekretariaduMixin

from .models import ApprovalStage, OutboundLetter


class OutboundLetterListView(LoginRequiredMixin, ListView):
    model = OutboundLetter
    template_name = "outbound_letters/letter_list.html"
    context_object_name = "letters"
    paginate_by = 25

    def get_queryset(self):
        qs = OutboundLetter.objects.select_related("created_by")
        user = self.request.user
        if user.role in [user.Role.ADMIN, user.Role.PREZIDENTE]:
            return qs
        return qs.filter(created_by=user)


class OutboundLetterCreateView(SekretariaduMixin, LoginRequiredMixin, CreateView):
    model = OutboundLetter
    template_name = "outbound_letters/letter_form.html"
    fields = [
        "subject", "recipient_name", "recipient_institution",
        "recipient_address", "original_ref_no", "letter_date",
        "pdf_file", "notes",
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
        context["can_dispatch"] = self.request.user.role == self.request.user.Role.ADMIN
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


class OutboundLetterDispatchView(AdminMixin, LoginRequiredMixin, UpdateView):
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
