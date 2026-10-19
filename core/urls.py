from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("pending-approval/", views.pending_approval, name="pending_approval"),
    path("admin-approvals/", views.admin_approvals, name="admin_approvals"),
    path("admin-approvals/<str:kind>/<int:pk>/<str:action>/",
         views.admin_approve_action, name="admin_approve_action"),
]
