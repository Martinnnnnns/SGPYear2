from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from datetime import timedelta
from tutorials.models import User, ProgrammingLanguage, Subject, LessonRequest, Lesson
import uuid

class TriggerMatchingTestCase(TestCase):
    def setUp(self):
        # Set up URLs
        self.url = reverse('trigger_matching')

        # Create users
        self.admin_user = User.objects.create_user(
            username="@admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="Password123",
            role="admin"
        )

        self.tutor = User.objects.create_user(
            username="tutor",
            email=f"tutor-{uuid.uuid4()}@example.com",
            first_name="Tutor",
            last_name="User",
            password="Password123",
            role="tutor"
        )

        self.student = User.objects.create_user(
            username="student",
            email=f"student-{uuid.uuid4()}@example.com",
            first_name="Student",
            last_name="User",
            password="Password123",
            role="student"
        )

        # Create a ProgrammingLanguage instance
        self.language = ProgrammingLanguage.objects.create(name="Python")

        # Create a Subject instance associated with the language
        self.subject = Subject.objects.create(name="Intro to Python", language=self.language)

        # Create a pending LessonRequest
        self.lesson_request = LessonRequest.objects.create(
            user=self.student,
            language=self.language,
            subject=self.subject,
            start_datetime=now() + timedelta(hours=1),  # Ensure future datetime
            end_datetime=now() + timedelta(hours=2),
        )

    def test_trigger_matching_url(self):
        """Test that the trigger matching URL resolves correctly."""
        self.assertEqual(self.url, '/trigger_matching/')  # Match the URL pattern

    def test_trigger_matching_requires_login(self):
        """Test that the view requires login."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_trigger_matching_as_admin(self):
        """Test that the view works as expected for admin users."""
        self.client.login(username="@admin", password="Password123")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

        # Verify the lesson was created
        self.assertEqual(Lesson.objects.count(), 1)
        lesson = Lesson.objects.first()
        self.assertEqual(lesson.student, self.student)
        self.assertEqual(lesson.tutor, self.tutor)

    def test_trigger_matching_no_tutors(self):
        """Test that no lesson is created if no tutors are available."""
        self.tutor.delete()  # Remove the tutor

        self.client.login(username="@admin", password="Password123")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

        # Verify no lessons were created
        self.assertEqual(Lesson.objects.count(), 0)

    def test_trigger_matching_template(self):
        """Test that the correct template is rendered."""
        self.client.login(username="@admin", password="Password123")
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, 'trigger_matching.html')