from django import forms
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


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "phone")


class ProfileView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"

    def get(self, request):
        user_form = UserProfileForm(instance=request.user)
        password_form = django.contrib.auth.forms.PasswordChangeForm(user=request.user)
        return django.shortcuts.render(request, self.template_name, {
            "user_form": user_form,
            "password_form": password_form,
        })

    def post(self, request):
        action = request.POST.get("action")
        user_form = UserProfileForm(instance=request.user)
        password_form = django.contrib.auth.forms.PasswordChangeForm(user=request.user)

        if action == "update_profile":
            user_form = UserProfileForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                django.contrib.messages.success(request, "Your profile details have been successfully updated.")
                return HttpResponseRedirect(reverse("monitoring:dashboard"))
        elif action == "change_password":
            password_form = django.contrib.auth.forms.PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                django.contrib.auth.update_session_auth_hash(request, password_form.user)
                django.contrib.messages.success(request, "Your password has been successfully changed.")
                return HttpResponseRedirect(reverse("monitoring:dashboard"))

        return django.shortcuts.render(request, self.template_name, {
            "user_form": user_form,
            "password_form": password_form,
        })


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
                    {"class": "h-4 w-4 text-red-700 focus:ring-[#900000] border-gray-300 rounded"}
                )
            else:
                field.widget.attrs.update(
                    {"class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#900000]"}
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
                    {"class": "h-4 w-4 text-red-700 focus:ring-[#900000] border-gray-300 rounded"}
                )
            else:
                field.widget.attrs.update(
                    {"class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#900000]"}
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
