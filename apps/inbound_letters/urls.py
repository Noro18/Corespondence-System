from django.urls import path

from . import views

app_name = "inbound_letters"

urlpatterns = [
    path("", views.InboundLetterListView.as_view(), name="list"),
    path("create/", views.InboundLetterCreateView.as_view(), name="create"),
    path("letters/<int:letter_pk>/assign/", views.AssignmentCreateView.as_view(), name="assign"),
    path("assignments/<int:pk>/update/", views.AssignmentUpdateView.as_view(), name="assignment_update"),
    path("<int:pk>/", views.InboundLetterDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", views.InboundLetterDeleteView.as_view(), name="delete"),
]
