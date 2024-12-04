from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from tutorials.models import (
    Lesson,
    ProgrammingLanguage,
    Subject,
    CancellationRequest,
    ChangeRequest
)
from tutorials.forms import CancellationRequestForm, ChangeBookingForm

User = get_user_model()


class BookingViewsTest(TestCase):
    def setUp(self):
        # Create Programming Language and Subject
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)

        # Create Users
        self.student = User.objects.create_user(
            username="student",
            password="Password123",
            email="student@example.com",
            role="student"
        )
        self.tutor = User.objects.create_user(
            username="tutor",
            password="Password123",
            email="tutor@example.com",
            role="tutor"
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
        self.completed_lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() - timedelta(days=1),
            status=Lesson.STATUS_COMPLETED
        )

        # URLs
        self.cancel_url = reverse("request_cancel_bookings", kwargs={"lesson_id": self.scheduled_lesson.id})
        self.change_url = reverse("request_change_bookings", kwargs={"lesson_id": self.scheduled_lesson.id})
        self.dashboard_url = reverse("dashboard")

        # Log in as the tutor
        self.client.login(username="tutor", password="Password123")

    # ----- Tests for Cancellation Views -----
    def test_successful_cancellation_view(self):
        """Test that a tutor can successfully cancel a scheduled lesson."""
        form_data = {
            "request_type": CancellationRequest.REQUEST_SINGLE,
            "lessons": [self.scheduled_lesson.id],
            "reason": "Need to cancel."
        }
        response = self.client.post(self.cancel_url, form_data, follow=True)
        self.scheduled_lesson.refresh_from_db()
        self.assertEqual(self.scheduled_lesson.status, Lesson.STATUS_CANCELED)
        self.assertRedirects(response, self.dashboard_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Your cancellation request has been submitted.")

    def test_cancellation_view_invalid_status(self):
        """Test that a tutor cannot cancel a completed lesson."""
        # Attempt to cancel a completed lesson
        cancel_url = reverse("request_cancel_bookings", kwargs={"lesson_id": self.completed_lesson.id})
        form_data = {
            "request_type": CancellationRequest.REQUEST_SINGLE,
            "lessons": [self.completed_lesson.id],
            "reason": "Attempting to cancel a completed lesson."
        }
        response = self.client.post(cancel_url, form_data, follow=True)
        self.completed_lesson.refresh_from_db()
        self.assertEqual(self.completed_lesson.status, Lesson.STATUS_COMPLETED)
        self.assertContains(response, "Completed lessons cannot be canceled.")

    def test_cancellation_view_permission_denied(self):
        """Test that a tutor cannot cancel another tutor's lesson."""
        # Create another tutor and a lesson for them
        other_tutor = User.objects.create_user(
            username="other_tutor",
            password="Password123",
            email="othertutor@example.com",
            role="tutor"
        )
        other_lesson = Lesson.objects.create(
            student=self.student,
            tutor=other_tutor,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() + timedelta(days=2),
            status=Lesson.STATUS_SCHEDULED
        )

        # Attempt to cancel other_tutor's lesson
        cancel_url = reverse("request_cancel_bookings", kwargs={"lesson_id": other_lesson.id})
        form_data = {
            "request_type": CancellationRequest.REQUEST_SINGLE,
            "lessons": [other_lesson.id],
            "reason": "Attempting to cancel another tutor's lesson."
        }
        response = self.client.post(cancel_url, form_data)
        other_lesson.refresh_from_db()
        self.assertEqual(other_lesson.status, Lesson.STATUS_SCHEDULED)
        self.assertContains(response, "You do not have permission to perform this action.")

    def test_cancellation_view_nonexistent_lesson(self):
        """Test that canceling a nonexistent lesson returns a 404."""
        nonexistent_id = self.scheduled_lesson.id + 100
        cancel_url = reverse("request_cancel_bookings", kwargs={"lesson_id": nonexistent_id})
        response = self.client.post(cancel_url, follow=True)
        self.assertEqual(response.status_code, 200)


    def test_reschedule_view_invalid_past_datetime(self):
        """Test that rescheduling to a past datetime is not allowed."""
        past_datetime = timezone.now() - timedelta(days=1)
        form_data = {
            "request_type": ChangeBookingForm.REQUEST_SINGLE,
            "lessons": [self.scheduled_lesson.id],
            "new_datetime": past_datetime.strftime('%Y-%m-%dT%H:%M'),
            "reason": "Invalid datetime."
        }
        response = self.client.post(self.change_url, form_data)
        self.scheduled_lesson.refresh_from_db()
        # Ensure datetime remains unchanged
        original_datetime = self.scheduled_lesson.lesson_datetime
        self.assertEqual(self.scheduled_lesson.lesson_datetime, original_datetime)
        self.assertContains(response, "The new date and time must be in the future.")

    def test_reschedule_view_permission_denied(self):
        """Test that a tutor cannot reschedule another tutor's lesson."""
        other_tutor = User.objects.create_user(
            username="other_tutor",
            password="Password123",
            email="othertutor@example.com",
            role="tutor"
        )
        other_lesson = Lesson.objects.create(
            student=self.student,
            tutor=other_tutor,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() + timedelta(days=2),
            status=Lesson.STATUS_SCHEDULED
        )
        change_url = reverse("request_change_bookings", kwargs={"lesson_id": other_lesson.id})
        form_data = {
            "request_type": ChangeBookingForm}