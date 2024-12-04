from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth import get_user_model
from tutorials.models import (
    Lesson,
    ProgrammingLanguage,
    Subject,
    CancellationRequest,
    ChangeRequest
)
from tutorials.forms import CancellationRequestForm, ChangeRequestForm

User = get_user_model()


class BookingFormsTest(TestCase):
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
        self.rescheduled_lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() + timedelta(days=2),
            status=Lesson.STATUS_RESCHEDULED
        )
        self.completed_lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() - timedelta(days=1),
            status=Lesson.STATUS_COMPLETED
        )

    # ----- Tests for CancellationRequestForm -----
    def test_cancellation_form_valid_single(self):
        """Test valid single cancellation by student."""
        form_data = {
            "request_type": 'single',
            "lessons": [self.scheduled_lesson.id],
            "reason": "Need to cancel."
        }
        form = CancellationRequestForm(data=form_data, user=self.student)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["lessons"].count(), 1)

    def test_cancellation_form_invalid_single_no_lessons(self):
        """Test invalid single cancellation with no lessons selected."""
        form_data = {
            "request_type": 'single',
            "lessons": [],
            "reason": "No lessons selected."
        }
        form = CancellationRequestForm(data=form_data, user=self.student)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'lessons', "Please select at least one lesson to cancel.")

    
    def test_cancellation_form_invalid_all_no_valid_lessons(self):
        """Test invalid all cancellations when no valid lessons exist."""
        # Update all lessons to completed
        Lesson.objects.filter(status__in=[Lesson.STATUS_SCHEDULED, Lesson.STATUS_RESCHEDULED]).update(status=Lesson.STATUS_COMPLETED)
        form_data = {
            "request_type": 'all',
            "reason": "Attempting to cancel all with no valid lessons."
        }
        form = CancellationRequestForm(data=form_data, user=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, None, "No valid lessons found to cancel.")

    # ----- Tests for ChangeRequestForm -----
    

    def test_change_request_form_invalid_single_no_lessons(self):
        """Test invalid single change with no lessons selected."""
        new_datetime = timezone.now() + timedelta(days=3)
        form_data = {
            "request_type": 'single',
            "lessons": [],
            "new_datetime": new_datetime.strftime('%Y-%m-%dT%H:%M'),
            "reason": "No lessons selected."
        }
        form = ChangeRequestForm(data=form_data, user=self.student)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'lessons', "Please select at least one lesson to change.")

    def test_change_request_form_invalid_past_datetime(self):
        """Test that change cannot be made to a past datetime."""
        past_datetime = timezone.now() - timedelta(days=1)
        form_data = {
            "request_type": 'single',
            "lessons": [self.scheduled_lesson.id],
            "new_datetime": past_datetime.strftime('%Y-%m-%dT%H:%M'),
            "reason": "Invalid datetime."
        }
        form = ChangeRequestForm(data=form_data, user=self.student)
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'new_datetime', "The new date and time must be in the future.")