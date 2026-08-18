from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.accounts.models import CustomUser
from apps.common.choices import LetterCategory
from apps.common.mixins import AdminMixin, PrezidenteMixin, SekretariaduMixin, StaffMixin
from apps.common.utils import export_csv_response

from .models import Assignment, InboundDecision, InboundLetter, Sender


class InboundLetterListView(LoginRequiredMixin, ListView):
    model = InboundLetter
    template_name = "inbound_letters/letter_list.html"
    context_object_name = "letters"
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = LetterCategory.choices
        return context

    def get_queryset(self):
        qs = InboundLetter.objects.select_related("sender", "registered_by").prefetch_related("assignments__assigned_to")
        user = self.request.user
        if user.role not in [user.Role.ADMIN, user.Role.PREZIDENTE, user.Role.SEKRETARIADU]:
            qs = qs.filter(assignments__assigned_to=user)
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs


class InboundLetterExportCSVView(LoginRequiredMixin, ListView):
    model = InboundLetter

    def get_queryset(self):
        qs = InboundLetter.objects.select_related("sender", "registered_by")
        user = self.request.user
        if user.role not in [user.Role.ADMIN, user.Role.PREZIDENTE, user.Role.SEKRETARIADU]:
            qs = qs.filter(assignments__assigned_to=user)
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs.distinct()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        headers = [
            "Tracking Code", "Original Ref No", "Subject", "Sender",
            "Category", "Letter Date", "Received Date", "Registered By", "Status"
        ]
        rows = []
        for l in queryset:
            rows.append([
                l.tracking_code,
                l.original_ref_no,
                l.title,
                l.sender.name if l.sender else "",
                l.get_category_display(),
                l.letter_date,
                l.received_date,
                l.registered_by.get_full_name() if l.registered_by else "",
                l.get_status_display(),
            ])
        return export_csv_response("inbound_letters.csv", headers, rows)


class InboundLetterCreateView(SekretariaduMixin, LoginRequiredMixin, CreateView):
    model = InboundLetter
    template_name = "inbound_letters/letter_form.html"
    fields = [
        "title", "original_ref_no", "sender", "letter_date",
        "pdf_file", "description", "notes", "category",
    ]
    extra_context = {"title": "Register Inbound Letter"}
    success_url = reverse_lazy("inbound_letters:list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["title"].label = "Subject"
        form.fields.pop("sender")
        form.fields["letter_date"].widget = forms.DateInput(
            attrs={"type": "date", "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"}
        )
        form.fields["sender_name"] = forms.CharField(
            max_length=255,
            label="Sender",
            widget=forms.TextInput(
                attrs={
                    "list": "senders-list",
                    "placeholder": "Type or select sender name",
                }
            ),
        )
        for field in form.fields.values():
            field.widget.attrs.setdefault("class",
                "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#900000]"
            )
            if field.required:
                field.widget.attrs["required"] = "required"
        return form

    def form_valid(self, form):
        name = form.cleaned_data["sender_name"].strip()
        sender, _ = Sender.objects.get_or_create(name=name)
        form.instance.sender = sender
        form.instance.registered_by = self.request.user
        return super().form_valid(form)


class InboundLetterUpdateView(SekretariaduMixin, LoginRequiredMixin, UpdateView):
    model = InboundLetter
    template_name = "inbound_letters/letter_form.html"
    fields = [
        "title", "original_ref_no", "sender", "letter_date",
        "pdf_file", "description", "notes", "category",
    ]
    context_object_name = "letter"
    extra_context = {"title": "Edit Inbound Letter"}

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == CustomUser.Role.ADMIN:
            return qs
        return qs.filter(registered_by=user).exclude(
            status__in=[InboundLetter.Status.COMPLETED, InboundLetter.Status.ARCHIVED]
        )

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["title"].label = "Subject"
        form.fields.pop("sender")
        form.fields["letter_date"].widget = forms.DateInput(
            attrs={"type": "date", "class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"}
        )
        form.fields["sender_name"] = forms.CharField(
            max_length=255,
            label="Sender",
            initial=self.object.sender.name,
            widget=forms.TextInput(
                attrs={
                    "list": "senders-list",
                    "placeholder": "Type or select sender name",
                }
            ),
        )
        form.fields["pdf_file"].required = False
        for field in form.fields.values():
            field.widget.attrs.setdefault("class",
                "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#900000]"
            )
            if field.required:
                field.widget.attrs["required"] = "required"
        return form

    def form_valid(self, form):
        name = form.cleaned_data["sender_name"].strip()
        sender, _ = Sender.objects.get_or_create(name=name)
        form.instance.sender = sender
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("inbound_letters:detail", kwargs={"pk": self.object.pk})


class InboundLetterDetailView(LoginRequiredMixin, DetailView):
    model = InboundLetter
    template_name = "inbound_letters/letter_detail.html"
    context_object_name = "letter"

    def get_queryset(self):
        qs = InboundLetter.objects.select_related("sender", "registered_by").prefetch_related("assignments__assigned_to", "decisions__decided_by")
        user = self.request.user
        if user.role in [user.Role.ADMIN, user.Role.PREZIDENTE, user.Role.SEKRETARIADU]:
            return qs
        return qs.filter(assignments__assigned_to=user)


class InboundLetterDeleteView(AdminMixin, LoginRequiredMixin, DeleteView):
    model = InboundLetter
    template_name = "inbound_letters/letter_confirm_delete.html"
    success_url = reverse_lazy("inbound_letters:list")


class AssignmentCreateView(PrezidenteMixin, LoginRequiredMixin, CreateView):
    model = Assignment
    template_name = "inbound_letters/assignment_form.html"
    fields = ["assigned_to", "instructions", "due_date"]
    context_object_name = "assignment"

    def get_letter(self):
        return InboundLetter.objects.get(pk=self.kwargs["letter_pk"])

    def dispatch(self, request, *args, **kwargs):
        letter = self.get_letter()
        if (
            letter.category not in [LetterCategory.PEDIDU, LetterCategory.PROPOSTA]
            or letter.status != InboundLetter.Status.ACCEPTED
        ):
            return HttpResponseRedirect(reverse("inbound_letters:detail", kwargs={"pk": letter.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["letter"] = self.get_letter()
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["assigned_to"].queryset = CustomUser.objects.filter(
            role=CustomUser.Role.STAFF
        ).order_by("username")
        form.fields["due_date"].widget = forms.DateInput(attrs={"type": "date"})
        for field in form.fields.values():
            field.widget.attrs.setdefault("class",
                "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#900000]"
            )
        return form

    def form_valid(self, form):
        letter = self.get_letter()
        form.instance.letter = letter
        form.instance.assigned_by = self.request.user
        response = super().form_valid(form)
        letter.sync_status()
        return response

    def get_success_url(self):
        return reverse("inbound_letters:detail", kwargs={"pk": self.kwargs["letter_pk"]})


class AssignmentUpdateView(StaffMixin, LoginRequiredMixin, UpdateView):
    model = Assignment
    template_name = "inbound_letters/assignment_update.html"
    fields = ["status", "completion_report"]
    context_object_name = "assignment"

    def get_queryset(self):
        qs = Assignment.objects.select_related("letter", "assigned_to")
        if self.request.user.role == CustomUser.Role.ADMIN:
            return qs
        return qs.filter(assigned_to=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs.setdefault("class",
                "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#900000]"
            )
        return form

    def form_valid(self, form):
        self.object = form.save()
        if self.object.status == Assignment.Status.COMPLETED:
            self.object.completed_at = timezone.now()
            self.object.save(update_fields=["completed_at"])
        self.object.letter.sync_status()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("inbound_letters:detail", kwargs={"pk": self.object.letter.pk})


class InboundLetterDecisionView(PrezidenteMixin, LoginRequiredMixin, UpdateView):
    model = InboundLetter
    fields = []

    def get_queryset(self):
        return super().get_queryset().filter(
            status__in=[InboundLetter.Status.REGISTERED, InboundLetter.Status.REJECTED]
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        decision = request.POST.get("decision")
        if decision not in [
            InboundDecision.Decision.ACCEPTED,
            InboundDecision.Decision.REJECTED,
        ]:
            return HttpResponseRedirect(
                reverse("inbound_letters:detail", kwargs={"pk": self.object.pk})
            )
        self.object.status = {
            InboundDecision.Decision.ACCEPTED: InboundLetter.Status.ACCEPTED,
            InboundDecision.Decision.REJECTED: InboundLetter.Status.REJECTED,
        }[decision]
        self.object.save()
        InboundDecision.objects.create(
            letter=self.object,
            decision=decision,
            decided_by=request.user,
            comments=request.POST.get("comments", ""),
            decided_at=timezone.now(),
        )
        return HttpResponseRedirect(
            reverse("inbound_letters:detail", kwargs={"pk": self.object.pk})
        )


class InboundLetterArchiveView(PrezidenteMixin, LoginRequiredMixin, UpdateView):
    model = InboundLetter
    fields = []

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status = InboundLetter.Status.ARCHIVED
        self.object.save(update_fields=["status"])
        return HttpResponseRedirect(
            reverse("inbound_letters:detail", kwargs={"pk": self.object.pk})
        )
