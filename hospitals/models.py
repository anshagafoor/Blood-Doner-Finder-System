from django.conf import settings
from django.db import models
from django.utils import timezone
from accounts.constants import BLOOD_GROUPS, DISTRICTS


class ApprovalStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class HospitalProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="hospital_profile")
    hospital_name = models.CharField(max_length=150)
    district = models.CharField(max_length=40, choices=DISTRICTS)
    license_number = models.CharField(max_length=60)
    address = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=10, choices=ApprovalStatus.choices,
                                       default=ApprovalStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hospital_name

    @property
    def is_approved(self):
        return self.approval_status == ApprovalStatus.APPROVED


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


class DonorResponse(models.Model):
    """A donor's reply to an emergency blood request (two-way notification)."""

    class Reply(models.TextChoices):
        CAN_DONATE = "CAN_DONATE", "I can donate"
        CANT = "CANT", "Can't right now"

    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE,
                                      related_name="responses")
    donor = models.ForeignKey("donors.DonorProfile", on_delete=models.CASCADE,
                              related_name="request_responses")
    reply = models.CharField(max_length=12, choices=Reply.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blood_request", "donor")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.donor.full_name} -> {self.blood_request} ({self.get_reply_display()})"

    @property
    def can_donate(self):
        return self.reply == self.Reply.CAN_DONATE
