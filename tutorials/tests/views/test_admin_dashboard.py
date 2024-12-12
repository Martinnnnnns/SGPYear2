from django.urls import reverse
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import AdminMixin

class AdminDashboardTestCase(RoleSetupTest, AdminMixin):
    def setUp(self):
        self.setup_admin()
        self.url = reverse('dashboard')

    def test_dashboard_url(self):
        """Test the dashboard URL resolves correctly."""
        self.assertEqual(self.url, '/dashboard/')  

    def test_dashboard_view_renders(self):
        """Test the dashboard renders the correct template successfully."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')

    def test_dashboard_links(self):
        """Test the buttons link to the correct views."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(self.url, follow=True)
        html = response.content.decode('utf-8')

        '''
        student_list_url = reverse('admin_student_list')
        tutor_list_url = reverse('admin_tutor_list')
        bookings_list_url = reverse('admin_bookings_list')
        '''
        student_list_url = reverse('admin_list', kwargs={'list_type': 'students'})
        tutor_list_url = reverse('admin_list', kwargs={'list_type': 'tutors'})
        bookings_list_url = reverse('admin_list', kwargs={'list_type': 'bookings'})

        self.assertIn(f'href="{student_list_url}"', html)
        self.assertIn(f'href="{tutor_list_url}"', html)
        self.assertIn(f'href="{bookings_list_url}"', html)
        
    def test_dashboard_contains_buttons(self):
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, 'Students')
        self.assertContains(response, 'Tutors')
        self.assertContains(response, 'Bookings')
        
    def test_tutor_availability_button(self):
        """Test that the Tutor Availability button is present and links correctly."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, "Tutor Availability")
        self.assertContains(response, reverse("tutor_availability_list"))    
        
    