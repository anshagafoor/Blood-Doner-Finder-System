from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render, redirect

from accounts.models import User
from accounts.permissions import role_required
from donors.models import DonorProfile, DonationHistory
from hospitals.models import HospitalProfile, BloodRequest
from organizations.models import OrganizationProfile, DonationCamp
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
    if user.is_donor:
        return _donor_dashboard(request)
    if user.is_hospital:
        return _hospital_dashboard(request)
    if user.is_organization:
        return _org_dashboard(request)
    return render(request, "core/dashboard.html", {})


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
