from django.conf import settings
from django.db import models
from django.utils import timezone
from accounts.constants import DISTRICTS


class OrganizationProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="org_profile")
    org_name = models.CharField(max_length=150)
    district = models.CharField(max_length=40, choices=DISTRICTS)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.org_name


class DonationCamp(models.Model):
    organization = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE,
                                     related_name="camps")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    district = models.CharField(max_length=40, choices=DISTRICTS)
    location = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.title} ({self.date})"

    @property
    def is_upcoming(self):
        return self.date >= timezone.now().date()


class CampRegistration(models.Model):
    camp = models.ForeignKey(DonationCamp, on_delete=models.CASCADE, related_name="registrations")
    donor = models.ForeignKey("donors.DonorProfile", on_delete=models.CASCADE,
                              related_name="camp_registrations")
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("camp", "donor")

    def __str__(self):
        return f"{self.donor.full_name} -> {self.camp.title}"


class AwarenessProgram(models.Model):
    organization = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE,
                                     related_name="programs")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    date = models.DateField()
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title
