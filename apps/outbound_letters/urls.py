from django.urls import path

from . import views

app_name = "outbound_letters"

urlpatterns = [
    path("", views.OutboundLetterListView.as_view(), name="list"),
    path("export/", views.OutboundLetterExportCSVView.as_view(), name="export"),
    path("create/", views.OutboundLetterCreateView.as_view(), name="create"),
    path("<int:pk>/", views.OutboundLetterDetailView.as_view(), name="detail"),
    path("<int:pk>/review/<str:stage>/", views.OutboundLetterReviewView.as_view(), name="review"),
    path("<int:pk>/dispatch/", views.OutboundLetterDispatchView.as_view(), name="dispatch"),
    path("<int:pk>/delete/", views.OutboundLetterDeleteView.as_view(), name="delete"),
]
