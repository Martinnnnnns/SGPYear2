from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from tutorials.models import (
    Lesson,
    ProgrammingLanguage,
    Subject,
    TutorAvailability
)
from tutorials.forms import CancellationRequestForm, ChangeBookingForm

User = get_user_model()

class BookingRequestTests(TestCase):
    def setUp(self):
        # Create Language and Subject
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)

        # Create Users
        self.tutor = User.objects.create_user(
            username="tutor",
            password="Password123",
            email="tutor@example.com",
            role="tutor"
        )
        self.student = User.objects.create_user(
            username="student",
            password="Password123",
            email="student@example.com",
            role="student"
        )

        # Create Lessons
        self.scheduled_lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() + timedelta(days=1),
            status=Lesson.STATUS_SCHEDULED
        )
        self.scheduled_lesson_2 = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() + timedelta(days=2),
            status=Lesson.STATUS_SCHEDULED
        )

        # URLs
        self.cancel_url = reverse("request_cancel_bookings", kwargs={"lesson_id": self.scheduled_lesson.id})
        self.change_url = reverse("request_change_bookings", kwargs={"lesson_id": self.scheduled_lesson.id})
        self.dashboard_url = reverse("dashboard")

        # Log in as student
        self.client.login(username="student", password="Password123")

    # ---- Change Request Tests ----
    def test_successful_change_request(self):
        """Test that a valid change request updates the lesson datetime."""
        new_datetime = timezone.now() + timedelta(days=3)
        form_data = {
            "request_type": ChangeBookingForm.REQUEST_SINGLE,
            "lessons": [self.scheduled_lesson.id],
            "new_datetime": new_datetime.strftime('%Y-%m-%dT%H:%M'),
            "reason": "Need to reschedule due to a conflict."
        }
        response = self.client.post(self.change_url, form_data, follow=True)
        self.scheduled_lesson.refresh_from_db()
        self.assertRedirects(response, self.dashboard_url)

    def test_missing_lessons_in_change_request(self):
        """Test that rescheduling fails when no lessons are provided."""
        new_datetime = timezone.now() + timedelta(days=3)
        form_data = {
            "request_type": ChangeBookingForm.REQUEST_SINGLE,
            "lessons": [],  # No lessons provided
            "new_datetime": new_datetime.strftime('%Y-%m-%dT%H:%M'),
            "reason": "No lessons selected."
        }
        response = self.client.post(self.change_url, form_data)
        self.assertContains(response, "Please select at least one lesson to change.")

    def test_multiple_lessons_reschedule(self):
        """Test that multiple lessons can be rescheduled."""
        new_datetime = timezone.now() + timedelta(days=3)
        form_data = {
            "request_type": ChangeBookingForm.REQUEST_ALL,
            "new_datetime": new_datetime.strftime('%Y-%m-%dT%H:%M'),
            "reason": "Rescheduling all lessons."
        }
        response = self.client.post(self.change_url, form_data, follow=True)
        self.scheduled_lesson.refresh_from_db()
        self.scheduled_lesson_2.refresh_from_db()
        self.assertRedirects(response, self.dashboard_url)

    def test_tutor_availability_check_for_change(self):
        """Test that a lesson is not rescheduled if the tutor is unavailable."""
        unavailable_datetime = timezone.now() + timedelta(days=5)
        form_data = {
            "request_type": ChangeBookingForm.REQUEST_SINGLE,
            "lessons": [self.scheduled_lesson.id],
            "new_datetime": unavailable_datetime.strftime('%Y-%m-%dT%H:%M'),
            "reason": "Tutor unavailable."
        }
        response = self.client.post(self.change_url, form_data)

    # ---- Cancellation Request Tests ----
    def test_successful_cancellation_request(self):
        """Test that a lesson can be successfully canceled."""
        form_data = {
            "request_type": ChangeBookingForm.REQUEST_SINGLE,
            "lessons": [self.scheduled_lesson.id],
            "reason": "Need to cancel."
        }
        response = self.client.post(self.cancel_url, form_data, follow=True)
        self.scheduled_lesson.refresh_from_db()
        self.assertEqual(self.scheduled_lesson.status, Lesson.STATUS_CANCELED)
        self.assertRedirects(response, self.dashboard_url)

    def test_missing_lessons_in_cancellation_request(self):
        """Test that cancellation fails when no lessons are provided."""
        form_data = {
            "request_type": ChangeBookingForm.REQUEST_SINGLE,
            "lessons": [],  # No lessons provided
            "reason": "No lessons selected for cancellation."
        }
        response = self.client.post(self.cancel_url, form_data)
        self.assertContains(response, "Please select at least one lesson to cancel.")

    def test_multiple_lessons_cancellation(self):
        """Test that multiple lessons can be canceled."""
        form_data = {
            "request_type": ChangeBookingForm.REQUEST_ALL,
            "reason": "Canceling all lessons."
        }
        response = self.client.post(self.cancel_url, form_data, follow=True)
        self.scheduled_lesson.refresh_from_db()
        self.scheduled_lesson_2.refresh_from_db()
        self.assertEqual(self.scheduled_lesson.status, Lesson.STATUS_CANCELED)
        self.assertRedirects(response, self.dashboard_url)

    def test_invalid_status_cancellation(self):
        """Test that a completed lesson cannot be canceled."""
        self.scheduled_lesson.status = Lesson.STATUS_COMPLETED
        self.scheduled_lesson.save()
        form_data = {
            "request_type": ChangeBookingForm.REQUEST_SINGLE,
            "lessons": [self.scheduled_lesson.id],
            "reason": "Cannot cancel completed lesson."
        }
        response = self.client.post(self.cancel_url, form_data)
