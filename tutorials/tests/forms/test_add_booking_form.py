from django.test import TestCase
from django.core.exceptions import ValidationError
from tutorials.forms import AdminAddBookingForm
from tutorials.models import User, Lesson
from tutorials.models import ProgrammingLanguage, Subject
from datetime import datetime
from django.utils import timezone
from datetime import timedelta

from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin, TutorMixin


class AdminAddBookingFormTests(RoleSetupTest, StudentMixin, TutorMixin):
    def setUp(self):
        self.setup_student()
        self.setup_tutor()

        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)
 
        self.form_data = {
            'student': self.student_user,
            'tutor': self.tutor_user,
            'language': self.language,
            'subject': self.subject,
            'lesson_datetime': timezone.now() + timedelta(days=1),
            'status': Lesson.STATUS_SCHEDULED
        }

    def test_valid_form_data(self):
        """Test the form with valid data."""
        self.assertEquals(Lesson.objects.count(), 0) #No lessons present yet.
        form = AdminAddBookingForm(data=self.form_data)
        self.assertTrue(form.is_valid(), "The form should be valid with correct data.")
        form.save()
        self.assertEquals(Lesson.objects.count(), 1)

    def test_invalid_student_in_form_data(self):
        """Test the form raises a ValidationError for an invalid student."""
        self.student_user.roles.clear()  # Removes all roles from the user
        self.form_data["student"] = self.student_user
        
        self.assertEqual(Lesson.objects.count(), 0, "There should be no lessons before form submission.")
        form = AdminAddBookingForm(data=self.form_data)
        self.assertFalse(form.is_valid(), "The form should be invalid when the student role is missing.")
        self.assertIn("student", form.errors, "The form should have an error for the 'student' field.")
        self.assertNotEquals(form.errors.as_text, "")
        self.assertEqual(Lesson.objects.count(), 0, "No lessons should be created with invalid form data.")

    def test_invalid_tutor_in_form_data(self):
        """Test the form raises a ValidationError for non tutor user."""
        self.tutor_user.roles.clear()  
        self.form_data["tutor"] = self.tutor_user
        
        self.assertEqual(Lesson.objects.count(), 0, "There should be no lessons before form submission.")
        form = AdminAddBookingForm(data=self.form_data)
        self.assertFalse(form.is_valid(), "The form should be invalid when the tutor role is missing.")
        self.assertIn("tutor", form.errors, "The form should have an error for the 'tutor' field.")
        self.assertNotEquals(form.errors.as_text, "")
        self.assertEqual(Lesson.objects.count(), 0, "No lessons should be created with invalid form data.")

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
    

