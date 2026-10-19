from django.contrib import admin
from .models import OrganizationProfile, DonationCamp, CampRegistration, AwarenessProgram

@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = ("org_name", "district", "approval_status", "verified")
    list_filter = ("district", "approval_status", "verified")
    actions = ["approve_selected"]

    @admin.action(description="Approve selected organizations")
    def approve_selected(self, request, queryset):
        queryset.update(approval_status="APPROVED", verified=True)

@admin.register(DonationCamp)
class DonationCampAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "district", "date")
    list_filter = ("district", "date")

admin.site.register(CampRegistration)
admin.site.register(AwarenessProgram)
