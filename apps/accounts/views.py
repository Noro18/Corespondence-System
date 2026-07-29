from django.contrib.auth import logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.common.mixins import AdminMixin

from .models import CustomUser


import django.forms


class CustomLogoutView(View):
    def get(self, request):
        auth_logout(request)
        return HttpResponseRedirect(reverse("accounts:login"))


class CustomUserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "role", "phone", "department")


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "role", "phone", "department", "is_active")


class UserListView(AdminMixin, LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 25
    ordering = ["-is_active", "username"]


class UserCreateView(AdminMixin, LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "accounts/user_form.html"
    extra_context = {"title": "Add User"}
    success_url = reverse_lazy("accounts:user_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            if isinstance(field.widget, django.forms.CheckboxInput):
                field.widget.attrs.update(
                    {"class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"}
                )
            else:
                field.widget.attrs.update(
                    {"class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"}
                )
        return form


class UserUpdateView(AdminMixin, LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "accounts/user_form.html"
    extra_context = {"title": "Edit User"}
    success_url = reverse_lazy("accounts:user_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            if isinstance(field.widget, django.forms.CheckboxInput):
                field.widget.attrs.update(
                    {"class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"}
                )
            else:
                field.widget.attrs.update(
                    {"class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"}
                )
        return form


class UserDeleteView(AdminMixin, LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = "accounts/user_confirm_delete.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        return HttpResponseRedirect(self.get_success_url())
