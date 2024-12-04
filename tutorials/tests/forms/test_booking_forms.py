from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth import get_user_model
from tutorials.models import (
    Lesson,
    ProgrammingLanguage,
    Subject,
    CancellationRequest,
    ChangeRequest,
    User,
)
from tutorials.forms import CancellationRequestForm, ChangeRequestForm
User = get_user_model()
class BookingFormsTest(TestCase):
    def setUp(self):
        # Create Programming Language and Subject
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)

        # Create Users
        self.student_user = User.objects.create_user(
            username="student",
            password="Password123",
            email="student@example.com",
            role="student"
        )
        self.tutor_user = User.objects.create_user(
            username="tutor",
            password="Password123",
            email="tutor@example.com",
            role="tutor"
        )

        # Create Lessons
        self.lesson = Lesson.objects.create(
            student=self.student_user,
            tutor=self.tutor_user,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() + timedelta(days=1),
            status=Lesson.STATUS_SCHEDULED
        )

    def test_cancellation_request_form_valid(self):
        """Test the CancellationRequestForm with valid data."""
        form_data = {
            'request_type': CancellationRequest.REQUEST_SINGLE,
            'lessons': [self.lesson.id],
            'reason': 'Student needs to cancel due to personal reasons.',
        }
        form = CancellationRequestForm(data=form_data, user=self.student_user)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['lessons'].count(), 1)
        self.assertEqual(form.cleaned_data['reason'], form_data['reason'])

    def test_cancellation_request_form_invalid(self):
        """Test the CancellationRequestForm with missing required data."""
        form_data = {
            'request_type': CancellationRequest.REQUEST_SINGLE,
            'lessons': [],  # No lessons selected
            'reason': '',
        }
        form = CancellationRequestForm(data=form_data, user=self.student_user)
        self.assertFalse(form.is_valid())
        self.assertIn('lessons', form.errors)
        self.assertIn('Please select at least one lesson to cancel.', form.errors['lessons'])

    def test_change_request_form_valid(self):
        """Test the ChangeRequestForm with valid data."""
        new_datetime = timezone.now() + timedelta(days=2)
        form_data = {
            'lessons': [self.lesson.id],
            'new_datetime': new_datetime.strftime('%Y-%m-%dT%H:%M'),
            'reason': 'Rescheduling due to a conflict.',
        }
        form = ChangeRequestForm(data=form_data, user=self.student_user)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['new_datetime'], new_datetime)
        self.assertEqual(form.cleaned_data['reason'], form_data['reason'])

    def test_change_request_form_invalid_past_datetime(self):
        """Test the ChangeRequestForm with a past datetime."""
        past_datetime = timezone.now() - timedelta(days=1)
        form_data = {
            'lessons': [self.lesson.id],
            'new_datetime': past_datetime.strftime('%Y-%m-%dT%H:%M'),
            'reason': 'Invalid date test.',
        }
        form = ChangeRequestForm(data=form_data, user=self.student_user)
        self.assertFalse(form.is_valid())
        self.assertIn('new_datetime', form.errors)
        self.assertIn('The new date and time must be in the future.', form.errors['new_datetime'])

    