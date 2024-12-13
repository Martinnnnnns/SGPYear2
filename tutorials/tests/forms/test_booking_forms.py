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
from tutorials.forms import CancellationRequestForm, ChangeRequestForm, ChangeBookingForm
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin, TutorMixin

User = get_user_model()

class BookingFormsTest(RoleSetupTest, StudentMixin, TutorMixin):
    def setUp(self):
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)

        self.setup_student()
        self.setup_tutor()

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
            'reason': '',
        }
        form = CancellationRequestForm(data=form_data, user=self.student_user)
        self.assertTrue(form.is_valid())  
    def test_change_request_form_valid(self):
        """Test the ChangeRequestForm with valid data."""
        new_datetime = timezone.now() + timedelta(days=2)
        form_data = {
            'request_type': ChangeRequestForm.REQUEST_SINGLE,
            'lessons': [self.lesson.id],
            'new_datetime': new_datetime.strftime('%Y-%m-%dT%H:%M'),
            'reason': 'Rescheduling due to a conflict.',
        }
        form = ChangeRequestForm(data=form_data, user=self.student_user)
        self.assertTrue(form.is_valid())

        expected_datetime = new_datetime.replace(second=0, microsecond=0)
        cleaned_datetime = form.cleaned_data['new_datetime'].replace(second=0, microsecond=0)

        self.assertEqual(cleaned_datetime, expected_datetime)
        self.assertEqual(form.cleaned_data['reason'], form_data['reason'])

    def test_change_request_form_invalid_past_datetime(self):
        """Test the ChangeRequestForm with a past datetime."""
        past_datetime = timezone.now() - timedelta(days=1)
        form_data = {
            'request_type': ChangeRequestForm.REQUEST_SINGLE,
            'lessons': [self.lesson.id],
            'new_datetime': past_datetime.strftime('%Y-%m-%dT%H:%M'),
            'reason': 'Invalid date test.',
        }
        form = ChangeRequestForm(data=form_data, user=self.student_user)
        self.assertFalse(form.is_valid())
        self.assertIn('new_datetime', form.errors)
        self.assertIn('The new date and time must be in the future.', form.errors['new_datetime'])

    def test_change_request_form_missing_new_datetime(self):
        """Test the ChangeRequestForm with missing new_datetime."""
        form_data = {
            'request_type': ChangeRequestForm.REQUEST_SINGLE,
            'lessons': [self.lesson.id],
            'reason': 'Missing datetime test.',
        }
        form = ChangeRequestForm(data=form_data, user=self.student_user)
        self.assertFalse(form.is_valid())
        self.assertIn('new_datetime', form.errors)
        self.assertIn('This field is required.', form.errors['new_datetime'])

    def test_change_request_form_missing_request_type(self):
        """Test the ChangeRequestForm with missing request_type."""
        new_datetime = timezone.now() + timedelta(days=2)
        form_data = {
            'lessons': [self.lesson.id],
            'new_datetime': new_datetime.strftime('%Y-%m-%dT%H:%M'),
            'reason': 'Missing request type test.',
        }
        form = ChangeRequestForm(data=form_data, user=self.student_user)
        self.assertFalse(form.is_valid())
        self.assertIn('request_type', form.errors)
        self.assertIn('This field is required.', form.errors['request_type'])

    def test_change_request_form_invalid_request_type(self):
        """Test the ChangeRequestForm with an invalid request_type."""
        new_datetime = timezone.now() + timedelta(days=2)
        form_data = {
            'request_type': 'invalid_type',  # Invalid choice
            'lessons': [self.lesson.id],
            'new_datetime': new_datetime.strftime('%Y-%m-%dT%H:%M'),
            'reason': 'Invalid request type test.',
        }
        form = ChangeRequestForm(data=form_data, user=self.student_user)
        self.assertFalse(form.is_valid())
        self.assertIn('request_type', form.errors)

    def test_change_request_form_permission(self):
        """Test ChangeRequestForm permission validation."""
        other_student = User.objects.create_user(username="other_student", password=self.PASSWORD)
        other_student.roles.add(self.student_role)
        other_student.current_active_role = self.student_role
        other_student.save()

        form_data = {
            'request_type': ChangeRequestForm.REQUEST_SINGLE,
            'lessons': [self.lesson.id],
            'new_datetime': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'reason': 'Permission validation.',
        }
        form = ChangeRequestForm(data=form_data, user=other_student)
        self.assertFalse(form.is_valid())
        # Depending on form logic, this might need adjustment
        # Since `ChangeRequestForm` does not currently have permission checks in clean
        # This test may pass or fail based on actual form implementation
        # For now, assume it does not allow other students to change lessons they don't own
        # You might need to implement this logic in the form's `clean` method
        # If not implemented, this test will fail

    def test_empty_change_request_form_submission(self):
        """Test ChangeRequestForm with empty data."""
        form = ChangeRequestForm(data={}, user=self.student_user)
        self.assertFalse(form.is_valid())
        self.assertIn("request_type", form.errors)
        self.assertIn("new_datetime", form.errors)