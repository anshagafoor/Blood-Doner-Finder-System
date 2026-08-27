from django.contrib import admin
from .models import OrganizationProfile, DonationCamp, CampRegistration, AwarenessProgram

@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = ("org_name", "district", "verified")
    list_filter = ("district", "verified")

@admin.register(DonationCamp)
class DonationCampAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "district", "date")
    list_filter = ("district", "date")

admin.site.register(CampRegistration)
admin.site.register(AwarenessProgram)
