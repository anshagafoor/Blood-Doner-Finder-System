from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.permissions import role_required
from accounts.models import User
from notifications.models import notify, Notification
from rewards.services import record_donation_reward
from .models import DonorProfile, DonationHistory, DonationCertificate
from .forms import DonorProfileForm, DonorSearchForm, DonationCertificateForm


@login_required
def donor_search(request):
    """Search donors by blood group and district (login required for privacy)."""
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
    certificates = profile.certificates.all()
    return render(request, "donors/history.html",
                  {"profile": profile, "donations": donations, "certificates": certificates})


@role_required(User.Role.DONOR)
def upload_certificate(request):
    """Donor uploads a donation certificate (photo/PDF) for admin/hospital approval."""
    profile = get_object_or_404(DonorProfile, user=request.user)
    if request.method == "POST":
        form = DonationCertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.donor = profile
            cert.save()
            messages.success(
                request,
                "Certificate uploaded! It will count toward your donations once approved.")
            return redirect("donors:history")
    else:
        form = DonationCertificateForm()
    return render(request, "donors/upload_certificate.html", {"form": form})


def _can_review_certs(user):
    return user.is_authenticated and (user.is_admin_role or user.is_hospital)


@login_required
def cert_review(request):
    """Admin / hospital review queue for donation certificates."""
    if not _can_review_certs(request.user):
        messages.error(request, "You do not have permission to review certificates.")
        return redirect("core:dashboard")
    pending = DonationCertificate.objects.filter(
        status=DonationCertificate.Status.PENDING).select_related("donor")
    reviewed = DonationCertificate.objects.exclude(
        status=DonationCertificate.Status.PENDING).select_related("donor")[:20]
    return render(request, "donors/cert_review.html",
                  {"pending": pending, "reviewed": reviewed})


@login_required
def cert_action(request, pk, action):
    """Approve or reject a certificate. Approving creates a verified donation."""
    if not _can_review_certs(request.user):
        messages.error(request, "You do not have permission to do that.")
        return redirect("core:dashboard")
    cert = get_object_or_404(DonationCertificate, pk=pk)
    if cert.status != DonationCertificate.Status.PENDING:
        messages.info(request, "This certificate has already been reviewed.")
        return redirect("donors:cert_review")

    donor = cert.donor
    if action == "approve":
        cert.status = DonationCertificate.Status.APPROVED
        cert.reviewed_by = request.user
        cert.reviewed_at = timezone.now()
        cert.save(update_fields=["status", "reviewed_by", "reviewed_at"])
        # Create the verified donation record
        DonationHistory.objects.create(
            donor=donor, date=cert.donation_date, location=cert.location,
            units=cert.units, note="Verified via certificate", points_awarded=100,
        )
        donor.total_donations += 1
        if (not donor.last_donation_date) or cert.donation_date > donor.last_donation_date:
            donor.last_donation_date = cert.donation_date
        donor.save(update_fields=["total_donations", "last_donation_date"])
        record_donation_reward(donor)
        notify(donor.user, title="Donation certificate approved!",
               message=(f"Your donation on {cert.donation_date} was verified. "
                        f"You earned 100 points."),
               notification_type=Notification.Type.REWARD, link="/donors/me/history/")
        messages.success(request, f"Approved. {donor.full_name}'s donation is now verified.")
    elif action == "reject":
        cert.status = DonationCertificate.Status.REJECTED
        cert.reviewed_by = request.user
        cert.reviewed_at = timezone.now()
        cert.save(update_fields=["status", "reviewed_by", "reviewed_at"])
        notify(donor.user, title="Donation certificate not approved",
               message="Your uploaded certificate could not be verified. Please re-upload a clearer copy.",
               notification_type=Notification.Type.SYSTEM, link="/donors/me/history/")
        messages.info(request, "Certificate rejected.")
    return redirect("donors:cert_review")
