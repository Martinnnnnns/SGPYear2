from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from tutorials.models import Lesson, Subject, ProgrammingLanguage, User

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

        self.client.login(username='testuser', password='password123')

        self.language = ProgrammingLanguage.objects.create(name="Python")

        self.subject = Subject.objects.create(name="Django", language=self.language)

        self.lesson = Lesson.objects.create(
            student=self.user,
            tutor=self.user, 
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now()  
        )

    def test_lesson_detail_view(self):
        """Ensure the lesson detail view displays the correct information."""
        response = self.client.get(reverse('lesson_detail', args=[self.lesson.id]))
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'lesson_detail.html')  
        self.assertContains(response, self.lesson.subject.name)  
        self.assertContains(response, self.lesson.language.name)  