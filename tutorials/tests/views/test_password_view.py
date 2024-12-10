"""Tests for the password view."""
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from tutorials.forms import PasswordForm
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.helpers import reverse_with_next
from tutorials.tests.mixins import AdminMixin, StudentMixin, TutorMixin
from tutorials.views import PasswordView

class PasswordViewTest(RoleSetupTest, StudentMixin, TutorMixin, AdminMixin):
    """Test suite for the password view."""

    def setUp(self):
        self.setup_student()
        self.setup_tutor()
        self.setup_admin()
        self.url = reverse('password')
        self.form_input = {
            'password': RoleSetupTest.PASSWORD,
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }

    def test_password_url(self):
        self.assertEqual(self.url, '/password/')

    def test_get_password(self):
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))

    def test_get_password_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_password_change_unsuccesful_without_correct_old_password(self):
        self.client.login(username=self.student_user.username, password='Password123')
        self.form_input['password'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.student_user.refresh_from_db()
        is_password_correct = check_password('Password123', self.student_user.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccesful_without_password_confirmation(self):
        self.client.login(username=self.student_user.username, password='Password123')
        self.form_input['password_confirmation'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.student_user.refresh_from_db()
        is_password_correct = check_password('Password123', self.student_user.password)
        self.assertTrue(is_password_correct)

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        is_password_correct = check_password('Password123', self.student_user.password)
        self.assertTrue(is_password_correct)
        
    def test_successful_password_change_admin(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('dashboard')  
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')  
        self.admin_user.refresh_from_db()
        is_password_correct = check_password('NewPassword123', self.admin_user.password)
        self.assertTrue(is_password_correct)
    
    def test_successful_password_change_tutor(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('dashboard')  
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tutor_page.html')  
        self.tutor_user.refresh_from_db()
        is_password_correct = check_password('NewPassword123', self.tutor_user.password)
        self.assertTrue(is_password_correct)

    def test_successful_password_change_student(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('dashboard') 
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_dashboard.html')  
        self.student_user.refresh_from_db()
        is_password_correct = check_password('NewPassword123', self.student_user.password)
        self.assertTrue(is_password_correct)
        
    def test_get_success_url_for_admin(self):
        view = PasswordView()
        view.request = self.client.request().wsgi_request
        view.request.user = self.admin_user

        self.assertEqual(view.get_success_url(), reverse('dashboard'))

    def test_get_success_url_for_tutor(self):
        view = PasswordView()
        view.request = self.client.request().wsgi_request
        view.request.user = self.tutor_user

        self.assertEqual(view.get_success_url(), reverse('dashboard'))

    def test_get_success_url_for_student(self):
        view = PasswordView()
        view.request = self.client.request().wsgi_request
        view.request.user = self.student_user

        self.assertEqual(view.get_success_url(), reverse('dashboard'))
