from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from tutorials.models import Lesson, ProgrammingLanguage, User, Subject

class LessonTestCase(TestCase):
    def setUp(self):
        """Setup code for test database."""
        self.python = ProgrammingLanguage.objects.create(name="Python")
        self.flask = Subject.objects.create(name="Flask", language=self.python, description="Web development in Flask")
        self.general_subject = Subject.objects.create(name="General", language=self.python)
        
        # Mock users
        self.student = User.objects.create_user(username="@student123", email="student.thuwa@mail.com", password="Password123", first_name="Billy", last_name="Bob")    
        self.tutor = User.objects.create_user(username="@tutor123", email="tutor.jones@mail.com", password="Password123", first_name="Joe", last_name="Jones")

    def test_lesson_creation_with_subject(self):
        """Test that a lesson can be created with a valid subject and a datetime."""
        lesson_datetime = timezone.now()  # Set the datetime for the lesson
        lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.python,
            subject=self.flask,
            lesson_datetime=lesson_datetime
        )
        self.assertEqual(lesson.language.name, "Python")
        self.assertEqual(lesson.subject.name, "Flask")
        self.assertEqual(lesson.subject.language.name, "Python")
        self.assertEqual(lesson.lesson_datetime, lesson_datetime)

    def test_lesson_creation_without_subject(self):
        """Test that a lesson can be created without a subject (General) and with a datetime."""
        lesson_datetime = timezone.now()
        lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.python,
            subject=None,
            lesson_datetime=lesson_datetime
        )
        self.assertEqual(lesson.language.name, "Python")
        self.assertIsNone(lesson.subject)
        self.assertEqual(lesson.lesson_datetime, lesson_datetime)
        self.assertEqual(str(lesson), f"Python Lesson (General) at {lesson_datetime} between tutor {self.tutor.full_name()} and student {self.student.full_name()}")

    def test_subject_language_match(self):
        """Test that a lesson raises a ValidationError if the subject's language does not match the lesson's language."""
        javascript = ProgrammingLanguage.objects.create(name="JavaScript")
        javascript_subject = Subject.objects.create(name="React", language=javascript)

        # Creating a lesson with a subject that has a different language
        lesson = Lesson(
            student=self.student,
            tutor=self.tutor,
            language=self.python,
            subject=javascript_subject,
            lesson_datetime=timezone.now()  # Add lesson datetime to match the new field
        )
        
        # Check that validation fails when subject language doesn't match lesson language
        with self.assertRaises(ValidationError):
            lesson.clean()

    def test_get_language_method_with_subject(self):
        """Test that the get_language method returns the language from the subject."""
        lesson_datetime = timezone.now()
        lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.python,
            subject=self.flask,
            lesson_datetime=lesson_datetime
        )
        self.assertEqual(lesson.get_language(), self.flask.language)

    def test_get_language_method_without_subject(self):
        """Test that the get_language method returns the lesson's language when no subject is provided."""
        lesson_datetime = timezone.now()
        lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.python,
            subject=None,
            lesson_datetime=lesson_datetime
        )
        self.assertEqual(lesson.get_language(), self.python)

    def test_lesson_str_representation_with_datetime(self):
        """Test the string representation of a Lesson with datetime."""
        lesson_datetime = timezone.now()
        lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.python,
            subject=self.flask,
            lesson_datetime=lesson_datetime
        )
        # Check if the datetime is included in the string representation
        self.assertIn(str(lesson_datetime), str(lesson))
