from django.urls import path
from . import views

app_name = "donors"

urlpatterns = [
    path("search/", views.donor_search, name="search"),
    path("me/", views.my_profile, name="my_profile"),
    path("me/toggle-availability/", views.toggle_availability, name="toggle_availability"),
    path("me/history/", views.donation_history, name="history"),
    path("me/upload-certificate/", views.upload_certificate, name="upload_certificate"),
    path("certificates/review/", views.cert_review, name="cert_review"),
    path("certificates/<int:pk>/<str:action>/", views.cert_action, name="cert_action"),
    path("<int:pk>/", views.donor_detail, name="detail"),
]
