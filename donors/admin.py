from django.contrib import admin
from .models import DonorProfile, DonationHistory

@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "blood_group", "district", "is_available",
                    "total_donations", "total_points")
    list_filter = ("blood_group", "district", "is_available")
    search_fields = ("full_name", "user__username")

@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ("donor", "date", "location", "units", "points_awarded")
    list_filter = ("date",)
