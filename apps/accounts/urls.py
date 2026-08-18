from django.contrib.auth.views import LoginView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/create/", views.UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user_edit"),
    path("users/<int:pk>/password/", views.UserPasswordChangeView.as_view(), name="user_password_change"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user_delete"),
]
