from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.models import User
from accounts.permissions import role_required, account_approved
from donors.models import DonorProfile, DonationHistory
from hospitals.models import HospitalProfile, BloodRequest
from organizations.models import OrganizationProfile, DonationCamp
from notifications.models import notify, Notification
from accounts.constants import BLOOD_GROUPS


def home(request):
    stats = {
        "donors": DonorProfile.objects.count(),
        "hospitals": HospitalProfile.objects.count(),
        "organizations": OrganizationProfile.objects.count(),
        "donations": DonationHistory.objects.count(),
    }
    urgent = BloodRequest.objects.filter(
        status=BloodRequest.Status.OPEN).order_by("-created_at")[:4]
    return render(request, "core/home.html", {"stats": stats, "urgent": urgent})


@login_required
def dashboard(request):
    user = request.user
    if user.is_admin_role:
        return redirect("core:admin_dashboard")
    # Hospitals/organizations must be approved first
    if (user.is_hospital or user.is_organization) and not account_approved(user):
        return redirect("core:pending_approval")
    if user.is_donor:
        return _donor_dashboard(request)
    if user.is_hospital:
        return _hospital_dashboard(request)
    if user.is_organization:
        return _org_dashboard(request)
    return render(request, "core/dashboard.html", {})


@login_required
def pending_approval(request):
    """Shown to hospital/organization users whose account is not yet approved."""
    if account_approved(request.user):
        return redirect("core:dashboard")
    status = "PENDING"
    prof = getattr(request.user, "hospital_profile", None) or getattr(request.user, "org_profile", None)
    if prof:
        status = prof.approval_status
    return render(request, "core/pending_approval.html", {"status": status})


@role_required(User.Role.ADMIN)
def admin_approvals(request):
    """Admin screen: approve or reject pending hospitals and organizations."""
    from hospitals.models import ApprovalStatus as HAS
    hospitals = HospitalProfile.objects.all().order_by("approval_status", "-created_at")
    orgs = OrganizationProfile.objects.all().order_by("approval_status", "-created_at")
    pending_count = (hospitals.filter(approval_status="PENDING").count() +
                     orgs.filter(approval_status="PENDING").count())
    return render(request, "core/admin_approvals.html",
                  {"hospitals": hospitals, "orgs": orgs, "pending_count": pending_count})


@role_required(User.Role.ADMIN)
def admin_approve_action(request, kind, pk, action):
    """Approve or reject a hospital/organization account."""
    if kind == "hospital":
        prof = get_object_or_404(HospitalProfile, pk=pk)
        name = prof.hospital_name
    else:
        prof = get_object_or_404(OrganizationProfile, pk=pk)
        name = prof.org_name

    if action == "approve":
        prof.approval_status = "APPROVED"
        prof.verified = True
        prof.save(update_fields=["approval_status", "verified"])
        notify(prof.user, title="Account approved!",
               message=f"Your account '{name}' has been approved by the admin. You now have full access.",
               notification_type=Notification.Type.SYSTEM, link="/dashboard/")
        messages.success(request, f"{name} approved.")
    elif action == "reject":
        prof.approval_status = "REJECTED"
        prof.verified = False
        prof.save(update_fields=["approval_status", "verified"])
        notify(prof.user, title="Account not approved",
               message=f"Your account '{name}' was not approved. Please contact the administrator.",
               notification_type=Notification.Type.SYSTEM)
        messages.info(request, f"{name} rejected.")
    return redirect("core:admin_approvals")


def _donor_dashboard(request):
    profile = DonorProfile.objects.filter(user=request.user).first()
    recent_donations = profile.donations.all()[:5] if profile else []
    badges = profile.badges.select_related("badge")[:6] if profile else []
    open_requests = []
    if profile:
        from accounts.constants import COMPATIBILITY
        # requests this donor could help with
        matching = BloodRequest.objects.filter(
            district=profile.district, status=BloodRequest.Status.OPEN)
        open_requests = [r for r in matching
                         if profile.blood_group in COMPATIBILITY.get(r.blood_group, [])][:5]
    return render(request, "core/dashboard_donor.html", {
        "profile": profile, "recent_donations": recent_donations,
        "badges": badges, "open_requests": open_requests,
    })


def _hospital_dashboard(request):
    hospital = HospitalProfile.objects.filter(user=request.user).first()
    requests = hospital.requests.all() if hospital else []
    return render(request, "core/dashboard_hospital.html", {
        "hospital": hospital,
        "requests": requests[:6],
        "open_count": requests.filter(status=BloodRequest.Status.OPEN).count() if hospital else 0,
        "fulfilled_count": requests.filter(status=BloodRequest.Status.FULFILLED).count() if hospital else 0,
        "total_count": requests.count() if hospital else 0,
    })


def _org_dashboard(request):
    org = OrganizationProfile.objects.filter(user=request.user).first()
    camps = org.camps.all() if org else []
    programs = org.programs.all() if org else []
    return render(request, "core/dashboard_org.html", {
        "org": org, "camps": camps[:6], "programs": programs[:6],
        "camp_count": camps.count() if org else 0,
        "program_count": programs.count() if org else 0,
    })


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    # Blood group distribution
    bg_data = (DonorProfile.objects.values("blood_group")
               .annotate(count=Count("id")).order_by("blood_group"))
    bg_map = {row["blood_group"]: row["count"] for row in bg_data}
    blood_groups = [{"group": g[0], "count": bg_map.get(g[0], 0)} for g in BLOOD_GROUPS]
    max_bg = max([b["count"] for b in blood_groups], default=1) or 1

    # District distribution
    district_data = (DonorProfile.objects.values("district")
                     .annotate(count=Count("id")).order_by("-count")[:10])

    context = {
        "total_donors": DonorProfile.objects.count(),
        "total_hospitals": HospitalProfile.objects.count(),
        "total_orgs": OrganizationProfile.objects.count(),
        "total_requests": BloodRequest.objects.count(),
        "open_requests": BloodRequest.objects.filter(status=BloodRequest.Status.OPEN).count(),
        "fulfilled_requests": BloodRequest.objects.filter(status=BloodRequest.Status.FULFILLED).count(),
        "total_donations": DonationHistory.objects.count(),
        "total_camps": DonationCamp.objects.count(),
        "available_donors": DonorProfile.objects.filter(is_available=True).count(),
        "blood_groups": blood_groups,
        "max_bg": max_bg,
        "district_data": district_data,
        "recent_requests": BloodRequest.objects.all()[:8],
        "recent_donors": DonorProfile.objects.order_by("-created_at")[:8],
    }
    return render(request, "core/admin_dashboard.html", context)
