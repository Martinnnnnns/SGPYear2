from django.test import TestCase
from django.urls import reverse

class AdminListTestMixin:
    """Mixin for testing admin list views."""
    url_name = None  
    
    def setUp(self):
        self.url = reverse(self.url_name)

    def test_url_resolves_correctly(self):
        """Test that reverse resolves to the expected URL."""
        self.assertEqual(self.url, f'/{self.url_name}/')  # Adjust URL structure as needed

    def test_view_renders(self):
        """Test that the view renders successfully with the expected template."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.url_name}.html')

    def test_context_includes_page_obj(self):
        """Test that the view includes the page_obj in the context."""
        response = self.client.get(self.url)
        self.assertIn('page_obj', response.context)  # Verify pagination context exists


class AdminStudentListTestCase(AdminListTestMixin, TestCase):
    url_name = 'admin_student_list'


class AdminTutorListTestCase(AdminListTestMixin, TestCase):
    url_name = 'admin_tutor_list'


class AdminBookingsListTestCase(AdminListTestMixin, TestCase):
    url_name = 'admin_bookings_list'