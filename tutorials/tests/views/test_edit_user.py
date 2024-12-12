from django.test import TestCase
from django.urls import reverse
from tutorials.models import User
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import AdminMixin, StudentMixin

class UpdateUserTests(RoleSetupTest, AdminMixin, StudentMixin):
    def setUp(self):
        self.setup_admin()
        self.setup_student()
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD) 

    def test_edit_user_view_get(self):
        """Test GET request for editing a user."""
        url = reverse('update_user', kwargs={'email': self.student_user.email})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit profile')
        self.assertEqual(response.context['user'], self.student_user)

    def test_edit_user_view_post(self):
        """Test POST request for editing a user."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)  
        valid_data = {
            'username': '@updateduser',
            'email': 'updateduser@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'password': 'newpassword123',
        }

        url = reverse('update_user', kwargs={'email': self.student_user.email})
        response = self.client.post(url, valid_data, follow=True)  

        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.username, '@updateduser')
        self.assertEqual(self.student_user.email, 'updateduser@example.com')
        self.assertTrue(self.student_user.check_password('newpassword123'))  


    def test_edit_user_view_invalid_data(self):
        """Test POST request with invalid data."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)  
        invalid_data = {
            'username': '',  
            'email': 'invaliduser@example.com',
            'first_name': 'Invalid',
            'last_name': 'User',
            'password': 'newpassword123',
        }

        url = reverse('update_user', kwargs={'email': self.student_user.email})
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, 200)  
        self.assertIn("This field is required.", str(response.content))
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.username, '@student')
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        