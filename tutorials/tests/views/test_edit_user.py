from django.urls import reverse
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import AdminMixin, TutorMixin

class UpdateUserTests(RoleSetupTest, AdminMixin, TutorMixin):
    def setUp(self):
        self.setup_admin()
        self.setup_tutor()
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD) 

    def test_edit_user_view_get(self):
        """Test GET request for editing a user."""
        url = reverse('update_record', kwargs={'email': self.tutor_user.email})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit profile')
        self.assertEqual(response.context['user'], self.tutor_user)

    def test_edit_user_view_post(self):
        """Test POST request for editing a user."""

        # Valid data for testing successful update
        valid_data = {
            'username': '@updateduser',
            'email': 'updateduser@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'password': 'newpassword123',
            'roles': [self.tutor_role.name]
        }

        url = reverse('update_record', kwargs={'email': self.tutor_user.email})
        response = self.client.post(url, valid_data, follow=True)  # follow=True to follow the redirect

        # Check if user was updated in the database
        self.tutor_user.refresh_from_db()
        self.assertEqual(self.tutor_user.username, '@updateduser')
        self.assertEqual(self.tutor_user.email, 'updateduser@example.com')
        self.assertTrue(self.tutor_user.check_password('newpassword123'))  # Check new password


    def test_edit_user_view_invalid_data(self):
        """Test POST request with invalid data."""
        invalid_data = {
            'username': '',  # Empty username
            'email': 'invaliduser@example.com',
            'first_name': 'Invalid',
            'last_name': 'User',
            'password': 'newpassword123',
        }

        url = reverse('update_record', kwargs={'email': self.tutor_user.email})
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, 200)  
        self.assertIn("This field is required.", str(response.content))
        self.tutor_user.refresh_from_db()
        self.assertEqual(self.tutor_user.username, '@testuser')
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        