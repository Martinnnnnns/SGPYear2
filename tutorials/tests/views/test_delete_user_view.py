from django.urls import reverse
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import AdminMixin, StudentMixin

class DeleteUserViewTests(RoleSetupTest, AdminMixin, StudentMixin):
    
    def setUp(self):
        self.setup_admin()  
        self.setup_student()

    def test_get_delete_user_view_as_admin(self):
        """Test admin can access the user deletion page."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)  
        url = reverse('delete_user', kwargs={'email': self.student_user.email})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'delete_user.html')
        self.assertContains(response, self.student_user.username)

    def test_get_delete_user_view_as_non_admin(self):
        """Test non-admin user is redirected when trying to access the delete user page."""
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)  
        url = reverse('delete_user', kwargs={'email': self.admin_user.email})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('access_denied'))
    
    def test_post_delete_user_view_as_admin(self):
        """Test admin can delete a user via POST."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)  
        url = reverse('delete_user', kwargs={'email': self.student_user.email})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('admin_list', kwargs={'list_type': 'students'}))

    def test_post_delete_user_view_as_non_admin(self):
        """Test non-admin user cannot delete a user."""
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)  
        url = reverse('delete_user', kwargs={'email': self.admin_user.email})
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('access_denied'))
        self.admin_user.refresh_from_db()
        self.assertIsNotNone(self.admin_user)
