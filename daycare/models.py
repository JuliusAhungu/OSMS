from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Child(models.Model):
	PROGRAM_CHOICES = [
		("toddlers", "Little Explorers · 1–2 years"),
		("early-years", "Curious Minds · 3–4 years"),
		("pre-primary", "Ready for School · 5–6 years"),
	]
	STATUS_CHOICES = [("active", "Active"), ("paused", "Paused"), ("graduated", "Graduated")]
	GENDER_CHOICES = [("girl", "Girl"), ("boy", "Boy")]

	first_name = models.CharField(max_length=80)
	last_name = models.CharField(max_length=80)
	birth_date = models.DateField(null=True, blank=True)
	gender = models.CharField(max_length=12, choices=GENDER_CHOICES, blank=True)
	program = models.CharField(max_length=20, choices=PROGRAM_CHOICES, default="early-years")
	parent_name = models.CharField(max_length=160)
	parent_phone = models.CharField(max_length=32)
	parent_email = models.EmailField(blank=True)
	allergies = models.TextField(blank=True)
	enrolled_on = models.DateField(default=timezone.localdate)
	status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="active")
	photo = models.ImageField(upload_to="children/", blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["first_name", "last_name"]

	def __str__(self):
		return f"{self.first_name} {self.last_name}"


class Inquiry(models.Model):
	class Status(models.TextChoices):
		NEW = "new", "New"
		CONTACTED = "contacted", "Contacted"
		ENROLLED = "enrolled", "Enrolled"
		CLOSED = "closed", "Closed"

	parent_name = models.CharField(max_length=160)
	child_name = models.CharField(max_length=160, blank=True)
	phone = models.CharField(max_length=32)
	email = models.EmailField(blank=True)
	child_age = models.CharField(max_length=40, blank=True)
	message = models.TextField()
	status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW)
	submitted_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-submitted_at"]

	def __str__(self):
		return f"{self.parent_name} · {self.submitted_at:%d %b %Y}"


class Attendance(models.Model):
	class Status(models.TextChoices):
		PRESENT = "present", "Present"
		ABSENT = "absent", "Absent"
		LATE = "late", "Late"
		EXCUSED = "excused", "Excused"

	child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="attendance_records")
	date = models.DateField(default=timezone.localdate)
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
	note = models.CharField(max_length=240, blank=True)
	recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		ordering = ["-date", "child__first_name"]
		constraints = [models.UniqueConstraint(fields=["child", "date"], name="unique_child_attendance_day")]

	def __str__(self):
		return f"{self.child} · {self.date} · {self.get_status_display()}"


class FeeRecord(models.Model):
	child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="fee_records")
	billing_period = models.CharField(max_length=80, help_text="For example: Term 1, 2026")
	due_date = models.DateField()
	amount_due = models.DecimalField(max_digits=10, decimal_places=2)
	amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["due_date", "child__first_name"]

	@property
	def balance(self):
		return max(self.amount_due - self.amount_paid, Decimal("0.00"))

	@property
	def state(self):
		if self.balance <= 0:
			return "Paid"
		if self.due_date < timezone.localdate():
			return "Overdue"
		return "Due"

	def __str__(self):
		return f"{self.child} · {self.billing_period}"


class Announcement(models.Model):
	title = models.CharField(max_length=160)
	body = models.TextField()
	published_at = models.DateTimeField(default=timezone.now)
	is_published = models.BooleanField(default=True)

	class Meta:
		ordering = ["-published_at"]

	def __str__(self):
		return self.title


class Event(models.Model):
	title = models.CharField(max_length=160)
	description = models.TextField(blank=True)
	date = models.DateField()
	starts_at = models.TimeField(null=True, blank=True)
	location = models.CharField(max_length=160, default="Shani Glorious Day Care Centre")
	is_published = models.BooleanField(default=True)

	class Meta:
		ordering = ["date", "starts_at"]

	def __str__(self):
		return f"{self.title} · {self.date}"


class StaffMember(models.Model):
	name = models.CharField(max_length=160)
	role = models.CharField(max_length=100)
	phone = models.CharField(max_length=32, blank=True)
	email = models.EmailField(blank=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return f"{self.name} · {self.role}"


class CareNote(models.Model):
	child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="care_notes")
	date = models.DateField(default=timezone.localdate)
	category = models.CharField(max_length=80, help_text="For example: nap, meal, health, or pickup")
	note = models.TextField()
	recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		ordering = ["-date", "child__first_name"]

	def __str__(self):
		return f"{self.child} · {self.category} · {self.date}"
