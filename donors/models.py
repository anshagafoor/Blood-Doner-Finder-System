from django.conf import settings
from django.db import models
from django.utils import timezone
from accounts.constants import BLOOD_GROUPS, DISTRICTS, GENDER_CHOICES


class DonorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="donor_profile")
    full_name = models.CharField(max_length=120)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    district = models.CharField(max_length=40, choices=DISTRICTS)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="M")
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True, blank=True)
    total_points = models.PositiveIntegerField(default=0)
    total_donations = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} - {self.blood_group}"

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def eligible_to_donate(self):
        """Eligible if never donated or >90 days since last donation."""
        if not self.last_donation_date:
            return True
        return (timezone.now().date() - self.last_donation_date).days >= 90


class DonationHistory(models.Model):
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE,
                              related_name="donations")
    date = models.DateField(default=timezone.now)
    location = models.CharField(max_length=150)
    units = models.PositiveSmallIntegerField(default=1)
    note = models.CharField(max_length=200, blank=True)
    blood_request = models.ForeignKey("hospitals.BloodRequest", null=True, blank=True,
                                      on_delete=models.SET_NULL, related_name="fulfilled_by")
    points_awarded = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.donor.full_name} donated on {self.date}"
