"""Business logic for points and badge awarding."""
from .models import Badge, DonorBadge, PointTransaction
from notifications.models import notify, Notification

POINTS_PER_DONATION = 100
POINTS_PER_CAMP = 20


def award_points(donor, points, reason):
    donor.total_points = (donor.total_points or 0) + points
    donor.save(update_fields=["total_points"])
    PointTransaction.objects.create(donor=donor, points=points, reason=reason)
    check_and_award_badges(donor)
    return points


def check_and_award_badges(donor):
    """Award any badge whose thresholds the donor now meets."""
    earned_ids = set(donor.badges.values_list("badge_id", flat=True))
    newly = []
    for badge in Badge.objects.all():
        if badge.id in earned_ids:
            continue
        if (donor.total_points >= badge.points_required and
                donor.total_donations >= badge.donations_required):
            DonorBadge.objects.create(donor=donor, badge=badge)
            newly.append(badge)
            notify(
                donor.user,
                title=f"New badge unlocked: {badge.name}!",
                message=f"Congratulations! You earned the '{badge.name}' badge. {badge.description}",
                notification_type=Notification.Type.REWARD,
                link="/rewards/my-rewards/",
            )
    return newly


def record_donation_reward(donor):
    """Called after a donation is logged: give points and refresh badges."""
    award_points(donor, POINTS_PER_DONATION, "Blood donation")
