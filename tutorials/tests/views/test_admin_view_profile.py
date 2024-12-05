from django.urls import reverse
from django.test import TestCase
from tutorials.models import User  # Import your custom User model here
from django.contrib.messages import get_messages


class AdminViewProfileTests(TestCase):
    
    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='@admin',
            password='adminpass',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin'  # Assuming the User model has a 'role' field
        )

        # Create a regular user
        self.student_user = User.objects.create_user(
            username='@student',
            password='studentpass',
            email='student@example.com',
            first_name='Student',
            last_name='User'
        )

    def test_admin_can_view_user_profile(self):
        """Test that an admin can view a user's profile."""
        self.client.login(username='@admin', password='adminpass')  # Log in as admin

        # URL for viewing the student's profile
        url = reverse('admin_view_profile', kwargs={'email': self.student_user.email})
        response = self.client.get(url)

        # Check that the status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used
        self.assertTemplateUsed(response, 'student_profile.html')

        # Check that the profile information is rendered correctly
        self.assertContains(response, self.student_user.first_name)
        self.assertContains(response, self.student_user.last_name)
        self.assertContains(response, self.student_user.email)
        self.assertContains(response, self.student_user.username)

    def test_non_admin_cannot_view_user_profile(self):
        """Test that a non-admin user cannot view a user's profile."""
        self.client.login(username='@student', password='studentpass')  # Log in as a non-admin

        # URL for viewing the admin's profile
        url = reverse('admin_view_profile', kwargs={'email': self.admin_user.email})
        response = self.client.get(url)

        # Check that the user is redirected (HTTP 302)
        self.assertEqual(response.status_code, 302)

        # Ensure the user is redirected to the access denied page
        self.assertRedirects(response, reverse('access_denied'))

