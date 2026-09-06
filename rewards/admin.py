from django.contrib import admin
from .models import Badge, DonorBadge, PointTransaction

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "points_required", "donations_required", "icon", "color")

@admin.register(DonorBadge)
class DonorBadgeAdmin(admin.ModelAdmin):
    list_display = ("donor", "badge", "awarded_at")

@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ("donor", "points", "reason", "created_at")
