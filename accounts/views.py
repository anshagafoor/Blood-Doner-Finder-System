from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import (DonorRegisterForm, HospitalRegisterForm,
                    OrganizationRegisterForm, LoginForm)
from .models import User
from donors.models import DonorProfile
from hospitals.models import HospitalProfile
from organizations.models import OrganizationProfile


def register_choice(request):
    return render(request, "accounts/register_choice.html")


def _finish(request, user):
    login(request, user)
    messages.success(request, f"Welcome, {user.username}! Your account is ready.")
    return redirect("core:dashboard")


def register_donor(request):
    if request.method == "POST":
        form = DonorRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.DONOR
            user.email = form.cleaned_data["email"]
            user.phone = form.cleaned_data["phone"]
            user.save()
            DonorProfile.objects.create(
                user=user,
                full_name=form.cleaned_data["full_name"],
                blood_group=form.cleaned_data["blood_group"],
                district=form.cleaned_data["district"],
                gender=form.cleaned_data["gender"],
                date_of_birth=form.cleaned_data["date_of_birth"],
                address=form.cleaned_data.get("address", ""),
            )
            return _finish(request, user)
    else:
        form = DonorRegisterForm()
    return render(request, "accounts/register_form.html",
                  {"form": form, "title": "Donor Registration", "accent": "donor"})


def register_hospital(request):
    if request.method == "POST":
        form = HospitalRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.HOSPITAL
            user.email = form.cleaned_data["email"]
            user.phone = form.cleaned_data["phone"]
            user.save()
            HospitalProfile.objects.create(
                user=user,
                hospital_name=form.cleaned_data["hospital_name"],
                district=form.cleaned_data["district"],
                license_number=form.cleaned_data["license_number"],
                address=form.cleaned_data["address"],
            )
            return _finish(request, user)
    else:
        form = HospitalRegisterForm()
    return render(request, "accounts/register_form.html",
                  {"form": form, "title": "Hospital Registration", "accent": "hospital"})


def register_organization(request):
    if request.method == "POST":
        form = OrganizationRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.ORGANIZATION
            user.email = form.cleaned_data["email"]
            user.phone = form.cleaned_data["phone"]
            user.save()
            OrganizationProfile.objects.create(
                user=user,
                org_name=form.cleaned_data["org_name"],
                district=form.cleaned_data["district"],
                address=form.cleaned_data["address"],
                website=form.cleaned_data.get("website", ""),
            )
            return _finish(request, user)
    else:
        form = OrganizationRegisterForm()
    return render(request, "accounts/register_form.html",
                  {"form": form, "title": "Organization Registration", "accent": "org"})


class AppLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("core:home")
