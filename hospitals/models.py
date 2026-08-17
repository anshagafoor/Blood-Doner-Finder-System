from django.conf import settings
from django.db import models
from django.utils import timezone
from accounts.constants import BLOOD_GROUPS, DISTRICTS


class HospitalProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="hospital_profile")
    hospital_name = models.CharField(max_length=150)
    district = models.CharField(max_length=40, choices=DISTRICTS)
    license_number = models.CharField(max_length=60)
    address = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hospital_name


class BloodRequest(models.Model):
    class Urgency(models.TextChoices):
        LOW = "LOW", "Low"
        NORMAL = "NORMAL", "Normal"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        FULFILLED = "FULFILLED", "Fulfilled"
        CANCELLED = "CANCELLED", "Cancelled"

    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE,
                                 related_name="requests")
    patient_name = models.CharField(max_length=120)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units_needed = models.PositiveSmallIntegerField(default=1)
    district = models.CharField(max_length=40, choices=DISTRICTS)
    urgency = models.CharField(max_length=10, choices=Urgency.choices, default=Urgency.NORMAL)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    contact_number = models.CharField(max_length=15)
    needed_by = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.blood_group} x{self.units_needed} for {self.patient_name}"

    @property
    def is_critical(self):
        return self.urgency == self.Urgency.CRITICAL
