from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .forms import ChildForm, FeeRecordForm, InquiryForm
from .models import Announcement, Attendance, Child, Event, FeeRecord, Inquiry


def home(request):
	form = InquiryForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		form.save()
		messages.success(request, "Thank you. Our team will be in touch soon.")
		return redirect("daycare:home")
	context = {
		"form": form,
		"programs": Child.PROGRAM_CHOICES,
		"announcements": Announcement.objects.filter(is_published=True)[:3],
		"events": Event.objects.filter(is_published=True, date__gte=date.today()).order_by("date")[:3],
		"children_count": Child.objects.filter(status="active").count(),
	}
	return render(request, "daycare/home.html", context)


class StaffLoginView(LoginView):
	template_name = "daycare/login.html"
	redirect_authenticated_user = True


class StaffLogoutView(LogoutView):
	next_page = reverse_lazy("daycare:home")


@staff_member_required(login_url="daycare:staff_login")
def dashboard(request):
	today = date.today()
	outstanding = FeeRecord.objects.filter(amount_paid__lt=F("amount_due"))
	context = {
		"children_count": Child.objects.filter(status="active").count(),
		"new_inquiries": Inquiry.objects.filter(status=Inquiry.Status.NEW).count(),
		"today_attendance": Attendance.objects.filter(date=today).values("status").annotate(total=Count("id")),
		"upcoming_events": Event.objects.filter(is_published=True, date__gte=today).order_by("date")[:4],
		"recent_inquiries": Inquiry.objects.order_by("-submitted_at")[:5],
		"fees_due": outstanding.select_related("child").order_by("due_date")[:5],
		"outstanding_total": sum((record.balance for record in outstanding), Decimal("0.00")),
		"today": today,
	}
	return render(request, "daycare/dashboard.html", context)


@staff_member_required(login_url="daycare:staff_login")
def children(request):
	query = request.GET.get("q", "").strip()
	child_list = Child.objects.all()
	if query:
		child_list = child_list.filter(
			Q(first_name__icontains=query)
			| Q(last_name__icontains=query)
			| Q(parent_name__icontains=query)
		)
	return render(request, "daycare/children.html", {"children": child_list, "query": query})


@staff_member_required(login_url="daycare:staff_login")
def child_form(request, pk=None):
	child = get_object_or_404(Child, pk=pk) if pk else None
	form = ChildForm(request.POST or None, request.FILES or None, instance=child)
	if request.method == "POST" and form.is_valid():
		form.save()
		messages.success(request, "Child record saved.")
		return redirect("daycare:children")
	return render(request, "daycare/child_form.html", {"form": form, "child": child})


@staff_member_required(login_url="daycare:staff_login")
@require_POST
def child_delete(request, pk):
	get_object_or_404(Child, pk=pk).delete()
	messages.success(request, "Child record removed.")
	return redirect("daycare:children")


@staff_member_required(login_url="daycare:staff_login")
def attendance(request):
	today = date.today()
	children_list = Child.objects.filter(status="active").order_by("first_name", "last_name")
	records = {record.child_id: record for record in Attendance.objects.filter(date=today)}
	attendance_rows = [
		{"child": child, "current_status": records[child.pk].status if child.pk in records else Attendance.Status.PRESENT}
		for child in children_list
	]
	if request.method == "POST":
		for child in children_list:
			status = request.POST.get(f"status-{child.pk}")
			if status in Attendance.Status.values:
				Attendance.objects.update_or_create(
					child=child, date=today, defaults={"status": status, "recorded_by": request.user}
				)
		messages.success(request, "Today's attendance has been saved.")
		return redirect("daycare:attendance")
	return render(
		request,
		"daycare/attendance.html",
		{"children": children_list, "attendance_rows": attendance_rows, "today": today, "statuses": Attendance.Status.choices},
	)


@staff_member_required(login_url="daycare:staff_login")
def fees(request, pk=None):
	record = get_object_or_404(FeeRecord, pk=pk) if pk else None
	form = FeeRecordForm(request.POST or None, instance=record)
	if request.method == "POST" and form.is_valid():
		form.save()
		messages.success(request, "Fee record saved.")
		return redirect("daycare:fees")
	return render(
		request,
		"daycare/fees.html",
		{"form": form, "record": record, "records": FeeRecord.objects.select_related("child").order_by("due_date")},
	)


@staff_member_required(login_url="daycare:staff_login")
def inquiries(request):
	return render(request, "daycare/inquiries.html", {"inquiries": Inquiry.objects.order_by("status", "-submitted_at")})


@staff_member_required(login_url="daycare:staff_login")
@require_POST
def inquiry_status(request, pk):
	inquiry = get_object_or_404(Inquiry, pk=pk)
	status = request.POST.get("status")
	if status in Inquiry.Status.values:
		inquiry.status = status
		inquiry.save(update_fields=["status"])
		messages.success(request, "Inquiry status updated.")
	return redirect("daycare:inquiries")
