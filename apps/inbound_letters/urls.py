from django.urls import path
from . import views

urlpatterns = [
    path("inbound/", views.inbound_list, name="inbound_list"),
    path("inbound/new/", views.inbound_create, name="inbound_create"),
    path("inbound/<int:pk>/", views.inbound_detail, name="inbound_detail"),
    path("senders/", views.sender_list, name="sender_list"),
    path("senders/new/", views.sender_create, name="sender_create"),
]
