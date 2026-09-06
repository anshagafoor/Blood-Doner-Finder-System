from django.shortcuts import render, get_object_or_404
from accounts.permissions import role_required
from accounts.models import User
from donors.models import DonorProfile
from .models import Badge, DonorBadge, PointTransaction


@role_required(User.Role.DONOR)
def my_rewards(request):
    donor = get_object_or_404(DonorProfile, user=request.user)
    earned = donor.badges.select_related("badge")
    earned_ids = set(earned.values_list("badge_id", flat=True))
    all_badges = Badge.objects.all()
    locked = [b for b in all_badges if b.id not in earned_ids]
    transactions = donor.point_transactions.all()[:20]
    # next badge to aim for
    next_badge = None
    for b in all_badges:
        if b.id not in earned_ids:
            next_badge = b
            break
    return render(request, "rewards/my_rewards.html", {
        "donor": donor, "earned": earned, "locked": locked,
        "transactions": transactions, "next_badge": next_badge,
    })


def leaderboard(request):
    top = DonorProfile.objects.order_by("-total_points", "-total_donations")[:20]
    return render(request, "rewards/leaderboard.html", {"top": top})
