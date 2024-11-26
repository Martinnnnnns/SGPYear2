from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import User
from django.utils import timezone

class LessonRequestViewTest(TestCase):
    def setUp(self):
        self.url = reverse("request_made")
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='testuser@example.com',
            first_name='John',
            last_name='Doe'
        )

        self.client.login(username='testuser', password='password123')

    def test_request_made_url(self):
        self.assertEqual(self.url, "/request_made/")

    def test_get_request_lesson(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "make_another_request.html")

    def test_load_make_lesson_request_page_again(self):
        make_another_url = reverse('request_lesson')
        response = self.client.get(make_another_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'make_lesson_request.html')

    def test_go_to_homepage(self):
        return_home_url = reverse('student_dashboard')
        response = self.client.get(return_home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_dashboard.html')
