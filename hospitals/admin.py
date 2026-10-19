from django.contrib import admin
from .models import HospitalProfile, BloodRequest, DonorResponse

@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):
    list_display = ("hospital_name", "district", "license_number",
                    "approval_status", "verified")
    list_filter = ("district", "approval_status", "verified")
    search_fields = ("hospital_name",)
    actions = ["approve_selected"]

    @admin.action(description="Approve selected hospitals")
    def approve_selected(self, request, queryset):
        queryset.update(approval_status="APPROVED", verified=True)

@admin.register(DonorResponse)
class DonorResponseAdmin(admin.ModelAdmin):
    list_display = ("donor", "blood_request", "reply", "created_at")
    list_filter = ("reply",)

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ("patient_name", "blood_group", "units_needed", "district",
                    "urgency", "status", "created_at")
    list_filter = ("blood_group", "urgency", "status", "district")
    search_fields = ("patient_name",)
