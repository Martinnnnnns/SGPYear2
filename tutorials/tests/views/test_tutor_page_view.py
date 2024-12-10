from django.urls import reverse
from tutorials.models import User
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin, TutorMixin

class TutorPageTestCase(RoleSetupTest, StudentMixin, TutorMixin):

    def setUp(self):
        self.url = reverse('dashboard')
        self.setup_student()
        self.setup_tutor()

    def test_tutor_page_url(self):
        self.assertEqual(self.url, reverse('dashboard'))

    def test_tutor_access(self):
        """Test that a user with the 'Tutor' role can access the tutor page."""
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_page.html') 

    def test_non_tutor_redirect(self):
        """Test that a user without the 'Tutor' role is redirected to the home page."""
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
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
        User.objects.all().delete()


    