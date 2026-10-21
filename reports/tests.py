
from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import override_settings
from .models import Report
from .matching import score_match
from .forms import SignupForm

@override_settings(COLLEGE_EMAIL_DOMAIN="campus.edu", COLLEGE_INVITE_CODE="")
class FindlyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student1", email="student1@campus.edu", password="StrongPass123!")
        self.other = User.objects.create_user(username="student2", email="student2@campus.edu", password="StrongPass123!")

    def test_signup_rejects_non_college_email(self):
        form = SignupForm(data={
            "first_name": "Test", "username": "testx", "email": "test@gmail.com",
            "password1": "StrongPass123!", "password2": "StrongPass123!", "invite_code": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_matching_opposite_report_types(self):
        lost = Report.objects.create(reporter=self.user, kind="LOST", title="Blue water bottle",
            description="steel bottle with sticker", category="Other", location="Library",
            item_date=date.today())
        found = Report.objects.create(reporter=self.other, kind="FOUND", title="Blue bottle",
            description="steel bottle with sticker", category="Other", location="Library",
            item_date=date.today())
        score, reasons = score_match(lost, found)
        self.assertGreaterEqual(score, 70)
        self.assertTrue(reasons)

    def test_report_requires_login(self):
        response = self.client.get(reverse("report_create"))
        self.assertEqual(response.status_code, 302)
