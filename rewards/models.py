from django.db import models
from django.utils import timezone


class Badge(models.Model):
    """A badge that is awarded when a donor reaches a points / donation threshold."""
    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=40, default="fa-award",
                            help_text="Font Awesome icon class, e.g. fa-award")
    color = models.CharField(max_length=20, default="#e63946")
    points_required = models.PositiveIntegerField(default=0)
    donations_required = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["points_required", "donations_required"]

    def __str__(self):
        return self.name


class DonorBadge(models.Model):
    donor = models.ForeignKey("donors.DonorProfile", on_delete=models.CASCADE,
                              related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="earned_by")
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("donor", "badge")
        ordering = ["-awarded_at"]

    def __str__(self):
        return f"{self.donor.full_name} - {self.badge.name}"


class PointTransaction(models.Model):
    donor = models.ForeignKey("donors.DonorProfile", on_delete=models.CASCADE,
                              related_name="point_transactions")
    points = models.IntegerField()
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.donor.full_name}: {self.points:+d} ({self.reason})"
