from django.urls import path

from . import views

app_name = "monitoring"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("export/", views.DashboardExportCSVView.as_view(), name="export"),
]
