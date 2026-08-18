from django import forms
from django.contrib import messages
from django.contrib.auth import logout as auth_logout, update_session_auth_hash
from django.contrib.auth.forms import (
    BaseUserCreationForm,
    PasswordChangeForm,
    ReadOnlyPasswordHashWidget,
    SetPasswordForm,
    UserChangeForm,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.common.mixins import AdminMixin

from .models import CustomUser

INPUT_CLASS = "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#900000]"
CHECKBOX_CLASS = "h-4 w-4 text-red-700 focus:ring-[#900000] border-gray-300 rounded"


def style_form_widgets(form):
    """Apply Tailwind CSS classes to every widget of the given form."""
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs.update({"class": CHECKBOX_CLASS})
        else:
            field.widget.attrs.update({"class": INPUT_CLASS})


class CustomLogoutView(View):
    def get(self, request):
        auth_logout(request)
        return HttpResponseRedirect(reverse("accounts:login"))


class CustomUserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "role", "phone", "department")


class PasswordLinkWidget(ReadOnlyPasswordHashWidget):
    """Read-only password hash widget with an explicit link to the password change page."""

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["password_url"] = attrs.pop("password_url", None)
        return context


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "role", "phone", "department", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get("password")
        if password:
            password.widget = PasswordLinkWidget(
                attrs={"password_url": reverse("accounts:user_password_change", args=[self.instance.pk])}
            )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "phone")


class ProfileView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"

    def get(self, request):
        user_form = UserProfileForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)
        return render(request, self.template_name, {
            "user_form": user_form,
            "password_form": password_form,
        })

    def post(self, request):
        action = request.POST.get("action")
        user_form = UserProfileForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)

        if action == "update_profile":
            user_form = UserProfileForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Your profile details have been successfully updated.")
                return HttpResponseRedirect(reverse("monitoring:dashboard"))
        elif action == "change_password":
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, "Your password has been successfully changed.")
                return HttpResponseRedirect(reverse("monitoring:dashboard"))

        return render(request, self.template_name, {
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
        style_form_widgets(form)
        return form


class UserUpdateView(AdminMixin, LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "accounts/user_form.html"
    extra_context = {"title": "Edit User"}
    success_url = reverse_lazy("accounts:user_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        style_form_widgets(form)
        return form


class UserPasswordChangeView(AdminMixin, LoginRequiredMixin, View):
    template_name = "accounts/user_password_form.html"

    def get_object(self, pk):
        return get_object_or_404(CustomUser, pk=pk)

    def get(self, request, pk):
        user = self.get_object(pk)
        form = SetPasswordForm(user=user)
        style_form_widgets(form)
        return render(request, self.template_name, {"form": form, "object": user})

    def post(self, request, pk):
        user = self.get_object(pk)
        form = SetPasswordForm(user=user, data=request.POST)
        style_form_widgets(form)
        if form.is_valid():
            form.save()
            if user.pk == request.user.pk:
                update_session_auth_hash(request, user)
            messages.success(request, f"Password for {user.username} has been set successfully.")
            return HttpResponseRedirect(reverse("accounts:user_list"))
        return render(request, self.template_name, {"form": form, "object": user})


class UserDeleteView(AdminMixin, LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = "accounts/user_confirm_delete.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        return HttpResponseRedirect(self.get_success_url())