from django.test import TestCase
from django.urls import reverse

class AdminDashboardTestCase(TestCase):
    
    def setUp(self):
        self.url = reverse('admin_dashboard')

    def test_dashboard_url(self):
        """Test that the dashboard URL resolves correctly."""
        self.assertEqual(self.url, '/admin_dashboard/')  

    def test_dashboard_view_renders(self):
        """Test the dashboard renders the correct template successfully."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')

    def test_dashboard_links(self):
        """Test that the buttons link to the correct views."""
        response = self.client.get(self.url)
        html = response.content.decode('utf-8')

        student_list_url = reverse('admin_student_list')
        tutor_list_url = reverse('admin_tutor_list')
        bookings_list_url = reverse('admin_bookings_list')

        self.assertIn(f'href="{student_list_url}"', html)
        self.assertIn(f'href="{tutor_list_url}"', html)
        self.assertIn(f'href="{bookings_list_url}"', html)
        
    def test_dashboard_contains_buttons(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Students')
        self.assertContains(response, 'Tutors')
        self.assertContains(response, 'Bookings')
