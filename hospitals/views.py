from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.permissions import role_required
from accounts.models import User
from accounts.constants import COMPATIBILITY
from donors.models import DonorProfile, DonationHistory
from notifications.models import notify, Notification, send_email_safe
from rewards.services import record_donation_reward
from .models import HospitalProfile, BloodRequest, DonorResponse
from .forms import BloodRequestForm, HospitalProfileForm


def _notify_eligible_donors(blood_request):
    """Notify compatible, available donors in the district (in-app + email)."""
    compatible_groups = COMPATIBILITY.get(blood_request.blood_group, [blood_request.blood_group])
    donors = DonorProfile.objects.filter(
        blood_group__in=compatible_groups,
        district=blood_request.district,
        is_available=True,
    )
    link = f"/hospitals/requests/{blood_request.id}/"
    message = (f"{blood_request.hospital.hospital_name} needs "
               f"{blood_request.units_needed} unit(s) of {blood_request.blood_group} "
               f"blood in {blood_request.district} "
               f"({blood_request.get_urgency_display()}). "
               f"Contact: {blood_request.contact_number}")
    count = 0
    for donor in donors:
        notify(
            donor.user,
            title=f"URGENT: {blood_request.blood_group} blood needed",
            message=message,
            notification_type=Notification.Type.EMERGENCY,
            link=link,
        )
        # Also send an emergency email (safe: never breaks the request)
        send_email_safe(
            donor.user,
            subject=f"URGENT: {blood_request.blood_group} blood needed in {blood_request.district}",
            message=(f"Dear {donor.full_name},\n\n{message}\n\n"
                     f"If you can help, please log in to BloodLink and respond to this request:\n"
                     f"  {link}\n\nThank you for saving lives.\n- BloodLink"),
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
            # 5.1 Send confirmation to the hospital
            notify(
                hospital.user,
                title="Blood request sent",
                message=(f"Your {br.blood_group} request for {br.patient_name} was sent to "
                         f"{notified} matching donor(s) in {br.district}."),
                notification_type=Notification.Type.SYSTEM,
                link=f"/hospitals/requests/{br.id}/",
            )
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
    responses = None
    my_response = None
    can_respond = False

    if request.user.is_authenticated and (request.user.is_hospital or request.user.is_admin_role):
        groups = COMPATIBILITY.get(br.blood_group, [br.blood_group])
        donors = DonorProfile.objects.filter(
            blood_group__in=groups, district=br.district, is_available=True)
        # 5.6 Responders list for the hospital/admin
        responses = br.responses.select_related("donor", "donor__user")

    if request.user.is_authenticated and request.user.is_donor:
        donor = DonorProfile.objects.filter(user=request.user).first()
        if donor:
            my_response = br.responses.filter(donor=donor).first()
            # A donor can respond if the request is still open and they match
            groups = COMPATIBILITY.get(br.blood_group, [br.blood_group])
            can_respond = (br.status == BloodRequest.Status.OPEN
                           and donor.blood_group in groups)

    return render(request, "hospitals/request_detail.html", {
        "br": br, "donors": donors, "responses": responses,
        "my_response": my_response, "can_respond": can_respond,
    })


@role_required(User.Role.DONOR)
def respond_to_request(request, pk):
    """5.3-5.5: Donor replies 'I can donate' / 'Can't right now' to an emergency request."""
    br = get_object_or_404(BloodRequest, pk=pk)
    donor = get_object_or_404(DonorProfile, user=request.user)
    if request.method == "POST":
        reply = request.POST.get("reply")
        if reply not in dict(DonorResponse.Reply.choices):
            messages.error(request, "Invalid response.")
            return redirect("hospitals:request_detail", pk=pk)

        resp, created = DonorResponse.objects.update_or_create(
            blood_request=br, donor=donor, defaults={"reply": reply})

        if reply == DonorResponse.Reply.CAN_DONATE:
            # 5.4 Notify the hospital that a donor can donate
            notify(
                br.hospital.user,
                title="A donor responded!",
                message=(f"{donor.full_name} ({donor.blood_group}) can donate for your "
                         f"{br.blood_group} request. Phone: {donor.user.phone or 'n/a'}, "
                         f"Email: {donor.user.email or 'n/a'}."),
                notification_type=Notification.Type.EMERGENCY,
                link=f"/hospitals/requests/{br.id}/",
            )
            send_email_safe(
                br.hospital.user,
                subject=f"Donor responded to your {br.blood_group} request",
                message=(f"{donor.full_name} ({donor.blood_group}) responded and can donate.\n"
                         f"Phone: {donor.user.phone or 'n/a'}\nEmail: {donor.user.email or 'n/a'}"),
            )
            # 5.5 Thank-you notification back to the donor
            notify(
                donor.user,
                title="Thank you for responding!",
                message=(f"You offered to donate for {br.hospital.hospital_name}'s "
                         f"{br.blood_group} request. The hospital has been informed and may contact you."),
                notification_type=Notification.Type.SYSTEM,
                link=f"/hospitals/requests/{br.id}/",
            )
            messages.success(request, "Thank you! The hospital has been notified that you can donate.")
        else:
            messages.info(request, "Thanks for letting us know. We've recorded your response.")
    return redirect("hospitals:request_detail", pk=pk)


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
