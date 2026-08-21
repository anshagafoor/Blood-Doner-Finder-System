from django.contrib import admin
from .models import HospitalProfile, BloodRequest

@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):
    list_display = ("hospital_name", "district", "license_number", "verified")
    list_filter = ("district", "verified")
    search_fields = ("hospital_name",)

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ("patient_name", "blood_group", "units_needed", "district",
                    "urgency", "status", "created_at")
    list_filter = ("blood_group", "urgency", "status", "district")
    search_fields = ("patient_name",)
