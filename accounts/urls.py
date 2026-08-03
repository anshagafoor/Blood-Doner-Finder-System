from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_choice, name="register"),
    path("register/donor/", views.register_donor, name="register_donor"),
    path("register/hospital/", views.register_hospital, name="register_hospital"),
    path("register/organization/", views.register_organization, name="register_organization"),
    path("login/", views.AppLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
]
