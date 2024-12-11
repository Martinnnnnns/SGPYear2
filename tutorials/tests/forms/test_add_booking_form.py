from django.test import TestCase
from django.core.exceptions import ValidationError
from tutorials.forms import AdminAddBookingForm
from tutorials.models import User, Lesson
from tutorials.models import ProgrammingLanguage, Subject
from datetime import datetime
from django.utils import timezone
from datetime import timedelta


class AdminAddBookingFormTests(TestCase):

    def setUp(self):
        # Create an existing user to test email uniqueness validation
        self.student = User.objects.create_user(
            username="student",
            password="Password123",
            email="student@example.com",
            current_active_role="student"
        )
        self.tutor = User.objects.create_user(
            username="tutor",
            password="Password123",
            email="tutor@example.com",
            current_active_role="tutor"
        )

        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)
 
    def test_valid_form_data(self):
        """Test the form with valid data."""
        form_data = {
            'student': self.student,
            'tutor': self.tutor,
            'language': self.language,
            'subject': self.subject,
            'lesson_datetime': timezone.now() + timedelta(days=1),
            'status': Lesson.STATUS_SCHEDULED
        }
        form = AdminAddBookingForm(data=form_data)
        self.assertTrue(form.is_valid(), "The form should be valid with correct data.")

    def test_missing_required_fields(self):
        """Test the form with missing required fields."""
        form_data = {
            'student': '',
            'tutor': '',
            'language': '',
            'subject': '',
            'lesson_datetime': '',
            'status': ''
        }
        form = AdminAddBookingForm(data=form_data)
        self.assertFalse(form.is_valid(), "The form should be invalid if required fields are missing.")
    

