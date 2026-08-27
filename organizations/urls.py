from django.urls import path
from . import views

app_name = "organizations"

urlpatterns = [
    path("camps/", views.camp_list, name="camp_list"),
    path("manage/", views.dashboard_camps, name="manage"),
    path("camps/new/", views.camp_create, name="camp_create"),
    path("awareness/new/", views.awareness_create, name="awareness_create"),
    path("camps/<int:pk>/register/", views.register_for_camp, name="camp_register"),
    path("profile/", views.org_profile, name="profile"),
]
