from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.permissions import role_required
from accounts.models import User
from donors.models import DonorProfile
from notifications.models import notify, Notification
from rewards.services import award_points, POINTS_PER_CAMP
from .models import (OrganizationProfile, DonationCamp,
                     CampRegistration, AwarenessProgram)
from .forms import CampForm, AwarenessForm, OrganizationProfileForm


def camp_list(request):
    """Public list of upcoming camps."""
    from django.utils import timezone
    camps = DonationCamp.objects.filter(date__gte=timezone.now().date())
    programs = AwarenessProgram.objects.all()[:6]
    return render(request, "organizations/camp_list.html",
                  {"camps": camps, "programs": programs})


@role_required(User.Role.ORGANIZATION)
def dashboard_camps(request):
    org = get_object_or_404(OrganizationProfile, user=request.user)
    camps = org.camps.all()
    programs = org.programs.all()
    return render(request, "organizations/manage.html",
                  {"org": org, "camps": camps, "programs": programs})


@role_required(User.Role.ORGANIZATION)
def camp_create(request):
    org = get_object_or_404(OrganizationProfile, user=request.user)
    if request.method == "POST":
        form = CampForm(request.POST)
        if form.is_valid():
            camp = form.save(commit=False)
            camp.organization = org
            camp.save()
            # Notify donors in the district
            donors = DonorProfile.objects.filter(district=camp.district)
            for d in donors:
                notify(d.user, title=f"New blood donation camp: {camp.title}",
                       message=f"{org.org_name} is organizing a camp at {camp.location} on {camp.date}.",
                       notification_type=Notification.Type.CAMP,
                       link="/organizations/camps/")
            messages.success(request, f"Camp created and {donors.count()} donors notified.")
            return redirect("organizations:manage")
    else:
        form = CampForm(initial={"district": org.district})
    return render(request, "organizations/camp_form.html", {"form": form})


@role_required(User.Role.ORGANIZATION)
def awareness_create(request):
    org = get_object_or_404(OrganizationProfile, user=request.user)
    if request.method == "POST":
        form = AwarenessForm(request.POST)
        if form.is_valid():
            program = form.save(commit=False)
            program.organization = org
            program.save()
            messages.success(request, "Awareness program added.")
            return redirect("organizations:manage")
    else:
        form = AwarenessForm()
    return render(request, "organizations/awareness_form.html", {"form": form})


@role_required(User.Role.DONOR)
def register_for_camp(request, pk):
    camp = get_object_or_404(DonationCamp, pk=pk)
    donor = get_object_or_404(DonorProfile, user=request.user)
    reg, created = CampRegistration.objects.get_or_create(camp=camp, donor=donor)
    if created:
        award_points(donor, POINTS_PER_CAMP, f"Registered for camp: {camp.title}")
        messages.success(request, f"Registered for {camp.title}. You earned {POINTS_PER_CAMP} points!")
    else:
        messages.info(request, "You are already registered for this camp.")
    return redirect("organizations:camp_list")


@role_required(User.Role.ORGANIZATION)
def org_profile(request):
    org = get_object_or_404(OrganizationProfile, user=request.user)
    if request.method == "POST":
        form = OrganizationProfileForm(request.POST, instance=org)
        if form.is_valid():
            form.save()
            messages.success(request, "Organization profile updated.")
            return redirect("organizations:profile")
    else:
        form = OrganizationProfileForm(instance=org)
    return render(request, "organizations/profile.html", {"form": form, "org": org})
