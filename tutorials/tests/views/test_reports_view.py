from django.test import TestCase
from django.urls import reverse
from tutorials.models import User

class ReportsViewTests(TestCase):
    def setUp(self):

        self.url = reverse('reports')
        # Create a tutor user
        self.tutor_user = User.objects.create_user(
            username='@tutor_user',
            password='testpassword123',
            email='tutor_user@example.com',
            role='tutor'
        )
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='@admin_user',
            password='testpassword123',
            email='admin_user@example.com',
            role='admin'
        )
        # Create a student user
        self.student_user = User.objects.create_user(
            username='@student_user',
            password='testpassword123',
            email='student_user@example.com',
            role='student'
        )

    def test_reports_url(self):
        self.assertEqual(self.url, reverse('reports'))

    def test_tutor_access_reports(self):
        """Test that a tutor can access the reports page."""
        self.client.login(username='@tutor_user', password='testpassword123')
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports.html')

    def test_admin_access_reports(self):
        """Test that an admin can access the reports page."""
        self.client.login(username='@admin_user', password='testpassword123')
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports.html')

    def test_non_authorised_user_redirect(self):
        """Test that a non-authorised user is redirected to their home page."""
        self.client.login(username='@student_user', password='testpassword123')
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 302)

    def test_login_required_reports(self):
        """Test that an unauthenticated user is redirected to the login page."""
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in/'))
        
    def tearDown(self):
        # Remove test users to clean up after the test
        """
        self.admin_user.delete()
        self.tutor_user.delete()
        self.student_user.delete()"""
        User.objects.all().delete()
