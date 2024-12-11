from django.test import TestCase
from django.urls import reverse
from tutorials.models import User

class UpdateUserTests(TestCase):
    def setUp(self):
        # Create an admin user 
        self.admin = User.objects.create_superuser(
            username='@admin', email='admin@example.com', password='adminpass', current_active_role='admin'
        )
        # Create a test user 
        self.user_to_update = User.objects.create_user(
            username='@testuser', email='testuser@example.com', password='password123'
        )

    def test_edit_user_view_get(self):
        """Test GET request for editing a user."""
        self.client.login(username='@admin', password='adminpass')

        url = reverse('update_record', kwargs={'email': self.user_to_update.email})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit profile')
        self.assertEqual(response.context['user'], self.user_to_update)

    def test_edit_user_view_post(self):
        """Test POST request for editing a user."""
        self.client.login(username='@admin', password='adminpass')

        # Valid data for testing successful update
        valid_data = {
            'username': '@updateduser',
            'email': 'updateduser@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'password': 'newpassword123',
            'current_active_role': 'tutor'
        }

        url = reverse('update_record', kwargs={'email': self.user_to_update.email})
        response = self.client.post(url, valid_data, follow=True)  # follow=True to follow the redirect

        # Check if user was updated in the database
        self.user_to_update.refresh_from_db()
        self.assertEqual(self.user_to_update.username, '@updateduser')
        self.assertEqual(self.user_to_update.email, 'updateduser@example.com')
        self.assertTrue(self.user_to_update.check_password('newpassword123'))  # Check new password


    def test_edit_user_view_invalid_data(self):
        """Test POST request with invalid data."""
        self.client.login(username='@admin', password='adminpass')

        # Invalid data (missing required field)
        invalid_data = {
            'username': '',  # Empty username
            'email': 'invaliduser@example.com',
            'first_name': 'Invalid',
            'last_name': 'User',
            'password': 'newpassword123',
        }

        url = reverse('update_record', kwargs={'email': self.user_to_update.email})
        response = self.client.post(url, invalid_data)

        self.assertEqual(response.status_code, 200)  
        
        # Check for specific validation message in the response content
        self.assertIn("This field is required.", str(response.content))

        self.user_to_update.refresh_from_db()
        self.assertEqual(self.user_to_update.username, '@testuser')
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        