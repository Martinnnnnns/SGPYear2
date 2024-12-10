"""Tests of the home view."""
from django.urls import reverse
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin

class HomeViewTestCase(RoleSetupTest, StudentMixin):
    """Tests of the home view."""

    def setUp(self):
        self.setup_student()
        self.url = reverse('home')

    def test_home_url(self):
        self.assertEqual(self.url,'/')

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_home_redirects_when_logged_in(self):
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_dashboard.html')
