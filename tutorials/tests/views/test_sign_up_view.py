"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from tutorials.forms import SignUpForm
from tutorials.models import User
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.helpers import LogInTester
from tutorials.tests.mixins import AdminMixin, StudentMixin, TutorMixin

class SignUpViewTestCase(RoleSetupTest, LogInTester, StudentMixin, AdminMixin, TutorMixin):
    """Tests of the sign up view."""
    def setUp(self):
        self.url = reverse('sign_up')

        self.admin_form_input = {
            'first_name': 'bob',
            'last_name': 'bobby',
            'username': '@admin',
            'email': 'bobby@gmail.com',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'roles': [self.admin_role.name]} 

        self.tutor_form_input = {
            'first_name': 'angela',
            'last_name': 'fred',
            'username': '@tutor',
            'email': 'angela@gmail.com',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'roles': [self.tutor_role.name]}

        self.student_form_input = {
            'first_name': 'liam',
            'last_name': 'smith',
            'username': '@student',
            'email': 'liam@gmail.com',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'roles': [self.student_role.name]} 

        self.setup_student()
        self.setup_tutor()
        self.setup_admin()


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
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')

    def test_get_sign_up_redirects_when_tutor_logged_in(self):
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tutor_page.html')

    def test_get_sign_up_redirects_when_student_logged_in(self):
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_dashboard.html')

    def test_unsuccesful_sign_up(self):
        self.student_form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.student_form_input)
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
        self.assertEqual(user.roles, [self.admin_role])  
        self.assertEqual(user.current_active_role, self.admin_role)
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
        self.assertEqual(user.roles, [self.tutor_role])  
        self.assertEqual(user.current_active_role, self.tutor_role)
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
        self.assertEqual(user.roles, [self.student_role]) 
        self.assertEqual(user.current_active_role, self.student_role)
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())

    def test_post_sign_up_redirects_when_admin_logged_in(self):
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        before_count = User.objects.count()
        response = self.client.post(self.url, self.admin_form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')
        
    def test_post_sign_up_redirects_when_tutor_logged_in(self):
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        before_count = User.objects.count()
        response = self.client.post(self.url, self.tutor_form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tutor_page.html')

    def test_post_sign_up_redirects_when_student_logged_in(self):
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        before_count = User.objects.count()
        response = self.client.post(self.url, self.student_form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_dashboard.html')

    