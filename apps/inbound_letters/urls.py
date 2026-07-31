from django.urls import path

from . import views

app_name = "inbound_letters"

urlpatterns = [
    path("", views.InboundLetterListView.as_view(), name="list"),
    path("create/", views.InboundLetterCreateView.as_view(), name="create"),
    path("<int:pk>/", views.InboundLetterDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", views.InboundLetterDeleteView.as_view(), name="delete"),
]
