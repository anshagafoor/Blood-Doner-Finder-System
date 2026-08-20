from django.urls import path
from . import views

app_name = "hospitals"

urlpatterns = [
    path("requests/", views.request_list, name="request_list"),
    path("requests/new/", views.request_create, name="request_create"),
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
    path("requests/<int:pk>/status/", views.request_update_status, name="request_status"),
    path("requests/<int:pk>/log-donation/", views.log_donation, name="log_donation"),
    path("profile/", views.hospital_profile, name="profile"),
]
