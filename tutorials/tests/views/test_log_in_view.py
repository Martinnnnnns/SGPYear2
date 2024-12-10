"""Tests of the log in view."""
from django.contrib import messages
from django.urls import reverse
from tutorials.forms import LogInForm
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.helpers import LogInTester, MenuTesterMixin, reverse_with_next
from tutorials.tests.mixins import AdminMixin, StudentMixin, TutorMixin

class LogInViewTestCase(RoleSetupTest, StudentMixin, TutorMixin, AdminMixin, LogInTester, MenuTesterMixin):
    """Tests of the log in view."""

    def setUp(self):
        self.url = reverse('log_in')
        self.setup_student()
        self.setup_tutor()
        self.setup_admin()

    def test_log_in_url(self):
        self.assertEqual(self.url,'/log_in/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(next)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        self.assert_no_menu(response)

    def test_get_log_in_with_redirect(self):
        destination_url = reverse('profile')
        self.url = reverse_with_next('log_in', destination_url)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertEqual(next, destination_url)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_unsuccesful_log_in(self):
        form_input = { 'username': self.student_user.username, 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_username(self):
        form_input = { 'username': '', 'password': 'Password123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_password(self):
        form_input = { 'username': '@student', 'password': '' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_valid_log_in_by_inactive_user(self):
        self.student_user.is_active = False
        self.student_user.save()
        form_input = { 'username': '@student', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_admin_login_redirect(self):
        response = self.client.post(reverse('log_in'), {'username': '@admin', 'password': 'Password123'}, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTemplateUsed(response, "admin_dashboard.html")

    def test_tutor_login_redirect(self):
        response = self.client.post(reverse('log_in'), {'username': '@tutor', 'password': 'Password123'}, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTemplateUsed(response, "tutor_page.html")

    def test_student_login_redirect(self):
        response = self.client.post(reverse('log_in'), {'username': '@student', 'password': 'Password123'}, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTemplateUsed(response, "student_dashboard.html")
        
  
    

