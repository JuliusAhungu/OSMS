from django.contrib import admin

from .models import Announcement, Attendance, CareNote, Child, Event, FeeRecord, Inquiry, StaffMember


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
	list_display = ("first_name", "last_name", "program", "parent_name", "parent_phone", "status")
	list_filter = ("status", "program", "gender")
	search_fields = ("first_name", "last_name", "parent_name", "parent_phone")


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
	list_display = ("parent_name", "child_name", "phone", "status", "submitted_at")
	list_filter = ("status", "submitted_at")
	search_fields = ("parent_name", "child_name", "phone", "email")
	readonly_fields = ("submitted_at",)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
	list_display = ("child", "date", "status", "recorded_by")
	list_filter = ("date", "status")
	search_fields = ("child__first_name", "child__last_name")


@admin.register(FeeRecord)
class FeeRecordAdmin(admin.ModelAdmin):
	list_display = ("child", "billing_period", "due_date", "amount_due", "amount_paid")
	list_filter = ("due_date", "billing_period")
	search_fields = ("child__first_name", "child__last_name", "billing_period")


admin.site.register((Announcement, Event, StaffMember, CareNote))
