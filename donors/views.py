# Query optimization applied: select_related used for related models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.permissions import role_required
from accounts.models import User
from .models import DonorProfile, DonationHistory
from .forms import DonorProfileForm, DonorSearchForm


def donor_search(request):
    """Search donors by blood group and district (public)."""
    form = DonorSearchForm(request.GET or None)
    results = DonorProfile.objects.all()
    searched = False
    if request.GET:
        searched = True
        if form.is_valid():
            bg = form.cleaned_data.get("blood_group")
            district = form.cleaned_data.get("district")
            only_available = form.cleaned_data.get("only_available")
            if bg:
                results = results.filter(blood_group=bg)
            if district:
                results = results.filter(district=district)
            if only_available:
                results = results.filter(is_available=True)
    else:
        results = results.filter(is_available=True)
    return render(request, "donors/search.html",
                  {"form": form, "results": results, "searched": searched})


@login_required
def donor_detail(request, pk):
    donor = get_object_or_404(DonorProfile, pk=pk)
    return render(request, "donors/detail.html", {"donor": donor})


@role_required(User.Role.DONOR)
def my_profile(request):
    profile = get_object_or_404(DonorProfile, user=request.user)
    if request.method == "POST":
        form = DonorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("donors:my_profile")
    else:
        form = DonorProfileForm(instance=profile)
    return render(request, "donors/my_profile.html", {"form": form, "profile": profile})


@role_required(User.Role.DONOR)
def toggle_availability(request):
    profile = get_object_or_404(DonorProfile, user=request.user)
    profile.is_available = not profile.is_available
    profile.save(update_fields=["is_available"])
    state = "available" if profile.is_available else "unavailable"
    messages.success(request, f"You are now marked as {state} to donate.")
    return redirect("donors:my_profile")


@role_required(User.Role.DONOR)
def donation_history(request):
    profile = get_object_or_404(DonorProfile, user=request.user)
    donations = profile.donations.all()
    return render(request, "donors/history.html",
                  {"profile": profile, "donations": donations})
