"""Role-based access decorators and mixins."""
from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def account_approved(user):
    """Hospitals and organizations must be admin-approved before they can operate.
    Donors, admins and superusers are always allowed."""
    if user.is_superuser:
        return True
    if user.is_hospital:
        prof = getattr(user, "hospital_profile", None)
        return bool(prof and prof.is_approved)
    if user.is_organization:
        prof = getattr(user, "org_profile", None)
        return bool(prof and prof.is_approved)
    return True


def role_required(*roles):
    """Allow access only to users whose role is in `roles` (superusers always pass).
    Hospital/organization users must also be approved by an admin."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser or request.user.role in roles:
                if not account_approved(request.user):
                    return redirect("core:pending_approval")
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to access that page.")
            return redirect("core:dashboard")
        return _wrapped
    return decorator
