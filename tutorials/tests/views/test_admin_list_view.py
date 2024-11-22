from django.test import TestCase
from django.urls import reverse
import pdb

from tutorials.models import User

class AdminListTestMixin:
    """Mixin for testing admin list views."""
    url_name = None  
    
    def setUp(self):
        self.url = reverse(self.url_name)
        self.admin_user = User.objects.create_user(email="bobby@gmail.com", first_name="bob", last_name="bobby", username='@admin', password='Password123', role='admin')

    def test_url_resolves_correctly(self):
        """Test that reverse resolves to the expected URL."""
        self.assertEqual(self.url, f'/{self.url_name}/')  # Adjust URL structure as needed

    def test_view_renders(self):
        """Test that the view renders successfully with the expected template."""
        self.client.login(username='@admin', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.url_name}.html')

    def tearDown(self):
        # Remove test users to clean up after the test
        #self.admin_user.delete()
        User.objects.all().delete()

class AdminStudentListTestCase(AdminListTestMixin, TestCase):
    url_name = 'admin_student_list'


class AdminTutorListTestCase(AdminListTestMixin, TestCase):
    url_name = 'admin_tutor_list'


class AdminBookingsListTestCase(AdminListTestMixin, TestCase):
    url_name = 'admin_bookings_list'
    
