from django.test import TestCase
from django.urls import reverse
from tutorials.models import User

class ScheduleSessionsViewTests(TestCase):
    def setUp(self):

        self.url = reverse('schedule_sessions')
        # Create a tutor user
        self.tutor_user = User.objects.create_user(
            username='@tutor_user',
            password='testpassword123',
            email='tutor_user@example.com',
            role='tutor'
        )
        # Create a student user
        self.student_user = User.objects.create_user(
            username='@student_user',
            password='testpassword123',
            email='student_user@example.com',
            role='student'
        )

    def test_schedule_sessions_url(self):
        self.assertEqual(self.url, reverse('schedule_sessions'))

    def test_tutor_access_schedule_sessions(self):
        """Test that a tutor can access the schedule sessions page."""
        self.client.login(username='@tutor_user', password='testpassword123')
        response = self.client.get(reverse('schedule_sessions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule_sessions.html')

    def test_non_tutor_redirect(self):
        """Test that a non-tutor user is redirected to the home page."""
        self.client.login(username='@student_user', password='testpassword123')
        response = self.client.get(reverse('schedule_sessions'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.templates, [])

    def test_login_required_schedule_sessions(self):
        """Test that an unauthenticated user is redirected to the login page."""
        response = self.client.get(reverse('schedule_sessions'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in/'))
        
    def tearDown(self):
        # Remove test users to clean up after the test
        """
        self.tutor_user.delete()
        self.student_user.delete()"""
        User.objects.all().delete()
