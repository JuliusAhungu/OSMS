from django.urls import path

from . import views

app_name = "daycare"

urlpatterns = [
    path("", views.home, name="home"),
    path("staff/login/", views.StaffLoginView.as_view(), name="staff_login"),
    path("staff/logout/", views.StaffLogoutView.as_view(), name="staff_logout"),
    path("staff/", views.dashboard, name="dashboard"),
    path("staff/children/", views.children, name="children"),
    path("staff/children/new/", views.child_form, name="child_create"),
    path("staff/children/<int:pk>/edit/", views.child_form, name="child_edit"),
    path("staff/children/<int:pk>/delete/", views.child_delete, name="child_delete"),
    path("staff/attendance/", views.attendance, name="attendance"),
    path("staff/fees/", views.fees, name="fees"),
    path("staff/fees/<int:pk>/edit/", views.fees, name="fee_edit"),
    path("staff/inquiries/", views.inquiries, name="inquiries"),
    path("staff/inquiries/<int:pk>/status/", views.inquiry_status, name="inquiry_status"),
]
