from django.contrib import messages
from django.urls import reverse
from tutorials.constants import UserRoles
from tutorials.forms import UserForm
from tutorials.models import User
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.helpers import reverse_with_next
from tutorials.tests.mixins import AdminMixin, StudentMixin, TutorMixin
from tutorials.views import ProfileUpdateView

class ProfileViewTest(RoleSetupTest, StudentMixin, TutorMixin, AdminMixin):
    def setUp(self):
        self.url = reverse('profile')
        self.setup_student()
        self.student_user.first_name = "John"
        self.student_user.last_name = "Doe"
        self.student_user.save()

        self.setup_tutor()
        self.setup_admin(

        )
        self.form_input = {
            'first_name': 'John2',
            'last_name': 'Doe2',
            'username': '@johndoe2',
            'email': 'johndoe2@example.org',
        }

        self.admin_form_input = {
            'first_name': 'bob',
            'last_name': 'bobby',
            'username': '@admin',
            'email': 'bobby@gmail.com',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
        }       
 
        self.tutor_form_input = {
            'first_name': 'angela',
            'last_name': 'fred',
            'username': '@tutor',
            'email': 'angela@gmail.com',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
        }

        self.student_form_input = {
            'first_name': 'liam',
            'last_name': 'smith',
            'username': '@student',
            'email': 'liam@gmail.com',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/profile/')

    def test_get_profile(self):
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertEqual(form.instance, self.student_user)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccesful_profile_update(self):
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        self.form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.username, '@student')
        self.assertEqual(self.student_user.first_name, 'John')
        self.assertEqual(self.student_user.last_name, 'Doe')
        self.assertEqual(self.student_user.email, 'student@example.com')

    def test_unsuccessful_profile_update_due_to_duplicate_username(self):
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        self.form_input['username'] = '@tutor'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.username, '@student')
        self.assertEqual(self.student_user.first_name, 'John')
        self.assertEqual(self.student_user.last_name, 'Doe')
        self.assertEqual(self.student_user.email, 'student@example.com')

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        
    def test_successful_profile_update_admin(self):
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        before_count = User.objects.count()
        response = self.client.post(self.url, self.admin_form_input, follow=True)
        after_count = User.objects.count()
        
        self.assertEqual(after_count, before_count)
        response_url = reverse('dashboard')  
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')  
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.username, '@admin')
        self.assertEqual(self.admin_user.first_name, 'bob')
        self.assertEqual(self.admin_user.last_name, 'bobby')
        self.assertEqual(self.admin_user.email, 'bobby@gmail.com')
        self.assertEqual(self.admin_user.current_active_role.name, UserRoles.ADMIN)
    
    def test_successful_profile_update_tutor(self):
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        before_count = User.objects.count()
        response = self.client.post(self.url, self.tutor_form_input, follow=True)
        after_count = User.objects.count()
        
        self.assertEqual(after_count, before_count)
        response_url = reverse('dashboard') 
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tutor_page.html') 
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        
        self.tutor_user.refresh_from_db()
        self.assertEqual(self.tutor_user.username, '@tutor')
        self.assertEqual(self.tutor_user.first_name, 'angela')
        self.assertEqual(self.tutor_user.last_name, 'fred')
        self.assertEqual(self.tutor_user.email, 'angela@gmail.com')
        self.assertEqual(self.tutor_user.current_active_role.name, UserRoles.TUTOR)
    
    def test_successful_profile_update_student(self):
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        before_count = User.objects.count()
        response = self.client.post(self.url, self.student_form_input, follow=True)
        after_count = User.objects.count()
        
        self.assertEqual(after_count, before_count)
        response_url = reverse('dashboard') 
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_dashboard.html')  
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.username, '@student')
        self.assertEqual(self.student_user.first_name, 'liam')
        self.assertEqual(self.student_user.last_name, 'smith')
        self.assertEqual(self.student_user.email, 'liam@gmail.com')
        self.assertEqual(self.student_user.current_active_role.name, UserRoles.STUDENT)
  
    def test_get_success_url_for_admin(self):
        view = ProfileUpdateView()
        view.request = self.client.request().wsgi_request
        view.request.user = self.admin_user

        self.assertEqual(view.get_success_url(), reverse('dashboard'))

    def test_get_success_url_for_tutor(self):
        view = ProfileUpdateView()
        view.request = self.client.request().wsgi_request
        view.request.user = self.tutor_user

        self.assertEqual(view.get_success_url(), reverse('dashboard'))

    def test_get_success_url_for_student(self):
        view = ProfileUpdateView()
        view.request = self.client.request().wsgi_request
        view.request.user = self.student_user

        self.assertEqual(view.get_success_url(), reverse('dashboard'))