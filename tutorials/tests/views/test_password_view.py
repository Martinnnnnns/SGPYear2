"""Tests for the password view."""
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tutorials.forms import PasswordForm
from tutorials.models import User
from tutorials.tests.helpers import reverse_with_next
from tutorials.views import PasswordView

class PasswordViewTest(TestCase):
    """Test suite for the password view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('password')
        self.form_input = {
            'password': 'Password123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }
        self.admin_user = User.objects.create_user(email="bobby@gmail.com", first_name="bob", last_name="bobby", username='@admin', password='Password123', role='admin')
        self.tutor_user = User.objects.create_user(email="angela@gmail.com",first_name="angela", last_name="fred",username='@tutor', password='Password123', role='tutor')
        self.student_user = User.objects.create_user(email="liam@gmail.com",first_name="liam", last_name="smith",username='@student', password='Password123', role='student')


    def test_password_url(self):
        self.assertEqual(self.url, '/password/')

    def test_get_password(self):
        self.client.login(username=self.user.username, password='Password123')
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
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['password'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccesful_without_password_confirmation(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['password_confirmation'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        is_password_correct = check_password('Password123', self.user.password)
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
