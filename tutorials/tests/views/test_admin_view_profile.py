from django.urls import reverse
from django.contrib.messages import get_messages
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import AdminMixin, StudentMixin

class AdminViewProfileTests(RoleSetupTest, StudentMixin, AdminMixin):
    
    def setUp(self):
        self.setup_admin()
        self.setup_student()

    def test_admin_can_view_user_profile(self):
        """Test admin can view a user's profile."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)

        url = reverse('admin_view_profile', kwargs={'email': self.student_user.email})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_profile.html')

        self.assertContains(response, self.student_user.first_name)
        self.assertContains(response, self.student_user.last_name)
        self.assertContains(response, self.student_user.email)
        self.assertContains(response, self.student_user.username)

    def test_non_admin_cannot_view_user_profile(self):
        """Test that a non-admin user cannot view a user's profile."""
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)  

        url = reverse('admin_view_profile', kwargs={'email': self.admin_user.email})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('access_denied'))

