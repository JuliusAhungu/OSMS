from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Attendance, Child, FeeRecord, Inquiry


class DaycareWorkflowTests(TestCase):
	def setUp(self):
		self.staff = get_user_model().objects.create_user(
			username="centre-staff", password="test-password", is_staff=True
		)

	def make_child(self):
		return Child.objects.create(
			first_name="Amina",
			last_name="Mushi",
			parent_name="Neema Mushi",
			parent_phone="+255 700 000 000",
		)

	def test_public_homepage_and_enquiry_submission(self):
		response = self.client.get(reverse("daycare:home"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "SHANI GLORIOUS DAY CARE CENTRE")

		response = self.client.post(
			reverse("daycare:home"),
			{
				"parent_name": "Neema Mushi",
				"child_name": "Amina Mushi",
				"phone": "+255 700 000 000",
				"email": "neema@example.com",
				"child_age": "3 years",
				"message": "I would like to arrange a visit.",
			},
		)
		self.assertRedirects(response, reverse("daycare:home"))
		self.assertEqual(Inquiry.objects.count(), 1)
		self.assertEqual(Inquiry.objects.get().status, Inquiry.Status.NEW)

	def test_staff_workspace_requires_staff_login(self):
		response = self.client.get(reverse("daycare:dashboard"))
		self.assertRedirects(response, f"{reverse('daycare:staff_login')}?next={reverse('daycare:dashboard')}")

		self.client.force_login(self.staff)
		for name in ("dashboard", "children", "attendance", "fees", "inquiries"):
			with self.subTest(page=name):
				self.assertEqual(self.client.get(reverse(f"daycare:{name}")).status_code, 200)

	def test_staff_can_create_child_and_mark_attendance(self):
		self.client.force_login(self.staff)
		response = self.client.post(
			reverse("daycare:child_create"),
			{
				"first_name": "Amina",
				"last_name": "Mushi",
				"gender": "girl",
				"program": "toddlers",
				"parent_name": "Neema Mushi",
				"parent_phone": "+255 700 000 000",
				"parent_email": "",
				"allergies": "",
				"enrolled_on": date.today().isoformat(),
				"status": "active",
			},
		)
		self.assertRedirects(response, reverse("daycare:children"))
		child = Child.objects.get(first_name="Amina")

		response = self.client.post(reverse("daycare:attendance"), {f"status-{child.pk}": "present"})
		self.assertRedirects(response, reverse("daycare:attendance"))
		self.assertEqual(Attendance.objects.get(child=child, date=date.today()).status, Attendance.Status.PRESENT)

	def test_staff_can_review_and_update_enquiry(self):
		inquiry = Inquiry.objects.create(
			parent_name="Neema Mushi",
			child_name="Amina",
			phone="+255 700 000 000",
			message="I would like to visit.",
		)
		self.client.force_login(self.staff)
		self.assertEqual(self.client.get(reverse("daycare:inquiries")).status_code, 200)

		response = self.client.post(
			reverse("daycare:inquiry_status", args=[inquiry.pk]),
			{"status": Inquiry.Status.CONTACTED},
		)
		self.assertRedirects(response, reverse("daycare:inquiries"))
		inquiry.refresh_from_db()
		self.assertEqual(inquiry.status, Inquiry.Status.CONTACTED)

	def test_staff_can_record_fee_and_balance_is_calculated(self):
		self.client.force_login(self.staff)
		child = self.make_child()
		response = self.client.post(
			reverse("daycare:fees"),
			{
				"child": child.pk,
				"billing_period": "Term 1, 2026",
				"due_date": (date.today() + timedelta(days=10)).isoformat(),
				"amount_due": "250000.00",
				"amount_paid": "100000.00",
			},
		)
		self.assertRedirects(response, reverse("daycare:fees"))
		fee = FeeRecord.objects.get(child=child)
		self.assertEqual(fee.balance, Decimal("150000.00"))
		self.assertEqual(fee.state, "Due")

		edit_url = reverse("daycare:fee_edit", args=[fee.pk])
		self.assertEqual(self.client.get(edit_url).status_code, 200)
		response = self.client.post(
			edit_url,
			{
				"child": child.pk,
				"billing_period": fee.billing_period,
				"due_date": fee.due_date.isoformat(),
				"amount_due": "250000.00",
				"amount_paid": "250000.00",
			},
		)
		self.assertRedirects(response, reverse("daycare:fees"))
		fee.refresh_from_db()
		self.assertEqual(fee.balance, Decimal("0.00"))
		self.assertEqual(fee.state, "Paid")
