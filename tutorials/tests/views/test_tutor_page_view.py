from django.test import TestCase
from django.urls import reverse
from tutorials.models import User

class TutorPageTestCase(TestCase):

    def setUp(self):
        self.url = reverse('dashboard')
        # Create a user with the 'Tutor' role
        self.tutor_user = User.objects.create_user(
            username='@tutor_user',
            password='testpassword123',
            email='tutor_user@example.com',
            first_name='Tutor',
            last_name='User',
            role=User.TUTOR
        )

        # Create a user with the 'Student' role
        self.student_user = User.objects.create_user(
            username='@student_user',
            password='testpassword123',
            email='student_user@example.com',
            first_name='Student',
            last_name='User',
            role=User.STUDENT
        )

    def test_tutor_page_url(self):
        self.assertEqual(self.url, reverse('dashboard'))

    def test_tutor_access(self):
        """Test that a user with the 'Tutor' role can access the tutor page."""
        self.client.login(username='@tutor_user', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_page.html') 

    def test_non_tutor_redirect(self):
        """Test that a user without the 'Tutor' role is redirected to the home page."""
        self.client.login(username='@student_user', password='testpassword123')
        response = self.client.get(reverse('dashboard')) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_dashboard.html')

    def test_login_required(self):
        """Test that an unauthenticated user is redirected to the login page."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in/'))

    def tearDown(self):
        # Remove test users to clean up after the test
        """
        self.admin_user.delete()
        self.tutor_user.delete()
        self.student_user.delete()
        self.user.delete()"""
        User.objects.all().delete()


    