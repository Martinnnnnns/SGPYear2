"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tutorials.forms import SignUpForm
from tutorials.models import User
from tutorials.tests.helpers import LogInTester

class SignUpViewTestCase(TestCase, LogInTester):
    """Tests of the sign up view."""

    fixtures = ['tutorials/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe',
            'email': 'janedoe@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'role': User.STUDENT
        }
        
        self.admin_form_input = {
            'first_name': 'bob',
            'last_name': 'bobby',
            'username': '@admin',
            'email': 'bobby@gmail.com',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'role': User.ADMIN
        }

        self.tutor_form_input = {
            'first_name': 'angela',
            'last_name': 'fred',
            'username': '@tutor',
            'email': 'angela@gmail.com',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'role': User.TUTOR
        }

        self.student_form_input = {
            'first_name': 'liam',
            'last_name': 'smith',
            'username': '@student',
            'email': 'liam@gmail.com',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'role': User.STUDENT
        }
        self.user = User.objects.get(username='@johndoe')
        self.admin_user = User.objects.create_user(email="bobby@gmail.com", first_name="bob", last_name="bobby", username='@admin', password='Password123', role='admin')
        self.tutor_user = User.objects.create_user(email="angela@gmail.com",first_name="angela", last_name="fred",username='@tutor', password='Password123', role='tutor')
        self.student_user = User.objects.create_user(email="liam@gmail.com",first_name="liam", last_name="smith",username='@student', password='Password123', role='student')


    def test_sign_up_url(self):
        self.assertEqual(self.url,'/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)
        
    def test_get_sign_up_redirects_when_admin_logged_in(self):
        self.client.login(username=self.admin_user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')

    def test_get_sign_up_redirects_when_tutor_logged_in(self):
        self.client.login(username=self.tutor_user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tutor_page.html')

    def test_get_sign_up_redirects_when_student_logged_in(self):
        self.client.login(username=self.student_user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_dashboard.html')

    def test_unsuccesful_sign_up(self):
        self.form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())
        
    def admin_test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.admin_form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('admin_dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')
        user = User.objects.get(username='@admin')
        self.assertEqual(user.first_name, 'bob')
        self.assertEqual(user.last_name, 'bobby')
        self.assertEqual(user.email, 'bobby@gmail.com')
        self.assertEqual(user.role, User.ADMIN)  # Test role assignment
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())

    def tutor_test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.tutor_form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('tutor_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tutor_page.html')
        user = User.objects.get(username='@tutor')
        self.assertEqual(user.first_name, 'angela')
        self.assertEqual(user.last_name, 'fred')
        self.assertEqual(user.email, 'angela@gmail.com')
        self.assertEqual(user.role, User.TUTOR)  # Test role assignment
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())

    def student_test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.student_form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')
        user = User.objects.get(username='@student')
        self.assertEqual(user.first_name, 'liam')
        self.assertEqual(user.last_name, 'smith')
        self.assertEqual(user.email, 'liam@gmail.com')
        self.assertEqual(user.role, User.STUDENT)  # Test role assignment
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())

    def test_post_sign_up_redirects_when_admin_logged_in(self):
        self.client.login(username=self.admin_user.username, password="Password123")
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')
        
    def test_post_sign_up_redirects_when_tutor_logged_in(self):
        self.client.login(username=self.tutor_user.username, password="Password123")
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tutor_page.html')

    def test_post_sign_up_redirects_when_student_logged_in(self):
        self.client.login(username=self.student_user.username, password="Password123")
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_dashboard.html')

    