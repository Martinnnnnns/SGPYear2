from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from tutorials.models import Lesson, Subject, ProgrammingLanguage

User = get_user_model()

class LessonDetailViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='testuser@example.com',
            first_name='John',
            last_name='Doe'
        )

        # Log the user in
        self.client.login(username='testuser', password='password123')

        # Create a programming language
        self.language = ProgrammingLanguage.objects.create(name="Python")

        # Create a subject with the same language as the lesson
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)

        # Create a lesson
        self.lesson = Lesson.objects.create(
            student=self.user,
            tutor=self.user,  # Assuming the same user can be a tutor for test purposes
            language=self.language,
            subject=self.subject,
            lesson_datetime=datetime.now()  # Providing a default datetime
        )

    def test_lesson_detail_view(self):
        """Ensure the lesson detail view displays the correct information."""
        response = self.client.get(reverse('lesson_detail', args=[self.lesson.id]))
        self.assertEqual(response.status_code, 200)  # Check if the page loads correctly
        self.assertTemplateUsed(response, 'lesson_detail.html')  # Verify the template used
        self.assertContains(response, self.lesson.subject.name)  # Verify subject is displayed
        self.assertContains(response, self.lesson.language.name)  # Verify language is displayed