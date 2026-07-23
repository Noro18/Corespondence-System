from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.common.mixins import AdminMixin

from .models import CustomUser


class UserListView(AdminMixin, LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 25
    ordering = ["-is_active", "username"]


class UserCreateView(AdminMixin, LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = UserCreationForm
    template_name = "accounts/user_form.html"
    extra_context = {"title": "Add User"}
    success_url = reverse_lazy("accounts:user_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field_name in form.fields:
            form.fields[field_name].widget.attrs.update(
                {"class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"}
            )
        return form


class UserUpdateView(AdminMixin, LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserChangeForm
    template_name = "accounts/user_form.html"
    extra_context = {"title": "Edit User"}
    success_url = reverse_lazy("accounts:user_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field_name in form.fields:
            form.fields[field_name].widget.attrs.update(
                {"class": "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"}
            )
        return form


class UserDeleteView(AdminMixin, LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = "accounts/user_confirm_delete.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        self.object.is_active = False
        self.object.save()
        return super().form_valid(form)
