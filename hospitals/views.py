from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.permissions import role_required
from accounts.models import User
from accounts.constants import COMPATIBILITY
from donors.models import DonorProfile, DonationHistory
from notifications.models import notify, Notification
from rewards.services import record_donation_reward
from .models import HospitalProfile, BloodRequest
from .forms import BloodRequestForm, HospitalProfileForm


def _notify_eligible_donors(blood_request):
    """Send emergency notifications to compatible, available donors in the district."""
    compatible_groups = COMPATIBILITY.get(blood_request.blood_group, [blood_request.blood_group])
    donors = DonorProfile.objects.filter(
        blood_group__in=compatible_groups,
        district=blood_request.district,
        is_available=True,
    )
    count = 0
    for donor in donors:
        notify(
            donor.user,
            title=f"URGENT: {blood_request.blood_group} blood needed",
            message=(f"{blood_request.hospital.hospital_name} needs "
                     f"{blood_request.units_needed} unit(s) of {blood_request.blood_group} "
                     f"blood in {blood_request.district} "
                     f"({blood_request.get_urgency_display()}). "
                     f"Contact: {blood_request.contact_number}"),
            notification_type=Notification.Type.EMERGENCY,
            link=f"/hospitals/requests/{blood_request.id}/",
        )
        count += 1
    return count


@role_required(User.Role.HOSPITAL)
def request_list(request):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    requests = hospital.requests.all()
    return render(request, "hospitals/request_list.html",
                  {"requests": requests, "hospital": hospital})


@role_required(User.Role.HOSPITAL)
def request_create(request):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    if request.method == "POST":
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            br = form.save(commit=False)
            br.hospital = hospital
            br.save()
            notified = _notify_eligible_donors(br)
            messages.success(
                request,
                f"Emergency request created. {notified} eligible donor(s) notified.")
            return redirect("hospitals:request_detail", pk=br.pk)
    else:
        form = BloodRequestForm(initial={"district": hospital.district})
    return render(request, "hospitals/request_form.html", {"form": form})


def request_detail(request, pk):
    br = get_object_or_404(BloodRequest, pk=pk)
    donors = None
    if request.user.is_authenticated and (request.user.is_hospital or request.user.is_admin_role):
        from accounts.constants import COMPATIBILITY
        groups = COMPATIBILITY.get(br.blood_group, [br.blood_group])
        donors = DonorProfile.objects.filter(
            blood_group__in=groups, district=br.district, is_available=True)
    return render(request, "hospitals/request_detail.html",
                  {"br": br, "donors": donors})


@role_required(User.Role.HOSPITAL)
def request_update_status(request, pk):
    br = get_object_or_404(BloodRequest, pk=pk, hospital__user=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(BloodRequest.Status.choices):
            br.status = new_status
            br.save(update_fields=["status", "updated_at"])
            messages.success(request, f"Request marked as {br.get_status_display()}.")
    return redirect("hospitals:request_detail", pk=pk)


@role_required(User.Role.HOSPITAL)
def log_donation(request, pk):
    """Record that a specific donor fulfilled a request -> award points + badge check."""
    br = get_object_or_404(BloodRequest, pk=pk, hospital__user=request.user)
    if request.method == "POST":
        donor_id = request.POST.get("donor_id")
        donor = get_object_or_404(DonorProfile, pk=donor_id)
        DonationHistory.objects.create(
            donor=donor,
            date=timezone.now().date(),
            location=br.hospital.hospital_name,
            units=1,
            note=f"Fulfilled request for {br.patient_name}",
            blood_request=br,
            points_awarded=100,
        )
        donor.total_donations += 1
        donor.last_donation_date = timezone.now().date()
        donor.save(update_fields=["total_donations", "last_donation_date"])
        record_donation_reward(donor)
        notify(donor.user, title="Thank you for donating!",
               message=f"Your donation at {br.hospital.hospital_name} was recorded. You earned 100 points.",
               notification_type=Notification.Type.REWARD)
        messages.success(request, f"Donation logged for {donor.full_name}. Points awarded.")
    return redirect("hospitals:request_detail", pk=pk)


@role_required(User.Role.HOSPITAL)
def hospital_profile(request):
    hospital = get_object_or_404(HospitalProfile, user=request.user)
    if request.method == "POST":
        form = HospitalProfileForm(request.POST, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, "Hospital profile updated.")
            return redirect("hospitals:profile")
    else:
        form = HospitalProfileForm(instance=hospital)
    return render(request, "hospitals/profile.html", {"form": form, "hospital": hospital})
