from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("donors/", include("donors.urls")),
    path("hospitals/", include("hospitals.urls")),
    path("organizations/", include("organizations.urls")),
    path("rewards/", include("rewards.urls")),
    path("notifications/", include("notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Blood Donor Finder Administration"
admin.site.site_title = "Blood Donor Finder Admin"
admin.site.index_title = "System Management"
