from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from apps.common.mixins import AdminMixin, SekretariaduMixin

from .models import InboundLetter, Sender


class InboundLetterListView(LoginRequiredMixin, ListView):
    model = InboundLetter
    template_name = "inbound_letters/letter_list.html"
    context_object_name = "letters"
    paginate_by = 25

    def get_queryset(self):
        qs = InboundLetter.objects.select_related("sender", "registered_by")
        user = self.request.user
        if user.role in [user.Role.ADMIN, user.Role.PREZIDENTE, user.Role.SEKRETARIADU]:
            return qs
        return qs.filter(assignments__assigned_to=user)


class InboundLetterCreateView(SekretariaduMixin, LoginRequiredMixin, CreateView):
    model = InboundLetter
    template_name = "inbound_letters/letter_form.html"
    fields = [
        "title", "original_ref_no", "sender", "letter_date",
        "pdf_file", "description", "notes",
    ]
    extra_context = {"title": "Register Inbound Letter"}
    success_url = reverse_lazy("inbound_letters:list")

    def form_valid(self, form):
        form.instance.registered_by = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
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
                "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            )
        return form


class InboundLetterDetailView(LoginRequiredMixin, DetailView):
    model = InboundLetter
    template_name = "inbound_letters/letter_detail.html"
    context_object_name = "letter"

    def get_queryset(self):
        qs = InboundLetter.objects.select_related("sender", "registered_by").prefetch_related("assignments__assigned_to")
        user = self.request.user
        if user.role in [user.Role.ADMIN, user.Role.PREZIDENTE, user.Role.SEKRETARIADU]:
            return qs
        return qs.filter(assignments__assigned_to=user)


class InboundLetterDeleteView(AdminMixin, LoginRequiredMixin, DeleteView):
    model = InboundLetter
    template_name = "inbound_letters/letter_confirm_delete.html"
    success_url = reverse_lazy("inbound_letters:list")
