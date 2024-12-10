from django.urls import reverse
from tutorials.models import User
from tutorials.tests.base import RoleSetupTest

class SetActiveRoleViewTest(RoleSetupTest):
    def setUp(self):
        """Set up a user with multiple roles."""
        self.user = User.objects.create_user(username='@testuser', password=RoleSetupTest.PASSWORD)
        self.user.roles.set([self.tutor_role, self.student_role])
        self.client.login(username="@testuser", password=RoleSetupTest.PASSWORD)

    def test_redirect_if_only_one_role(self):
        """Test redirect to dashboard when there is only one role."""
        self.user.roles.set([self.tutor_role])
        self.user.refresh_from_db()
        response = self.client.get(reverse('role_select'), follow=True)
        self.user.refresh_from_db()
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTemplateUsed("tutor_page.html")
        self.assertEqual(self.user.current_active_role, self.tutor_role)

    def test_show_role_selection_template(self):
        """Test template is shown when there are multiple roles."""
        response = self.client.get(reverse('role_select'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'set_active_role.html')
        self.assertIn('roles', response.context)
        expected_roles = [self.tutor_role, self.student_role]  
        actual_roles = list(response.context['roles']) 
        self.assertListEqual(actual_roles, expected_roles)

    def test_post_set_active_role_success(self):
        """Test successfully setting the active role."""
        response = self.client.post(reverse('role_select'), {'role': self.tutor_role.name})
        self.user.refresh_from_db()
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(self.user.current_active_role, self.tutor_role)

    def test_post_no_role_selected(self):
        """Test posting without selecting a role."""
        response = self.client.post(reverse('role_select'), {'role': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No role selected.")

    def test_post_invalid_role(self):
        """Test posting an invalid role."""
        response = self.client.post(reverse('role_select'), {'role': 'InvalidRole'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid role selection.")

    def test_post_change_active_role(self):
        """Test changing the active role."""
        self.user.current_active_role = self.tutor_role
        self.user.save()

        response = self.client.post(reverse('role_select'), {'role': self.student_role.name})
        self.user.refresh_from_db()

        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(self.user.current_active_role, self.student_role)
        self.assertTemplateUsed("student_dashboard.html")

    def test_post_keep_same_active_role(self):
        """Test submitting the same active role."""
        self.user.current_active_role = self.tutor_role
        self.user.save()

        response = self.client.post(reverse('role_select'), {'role': self.tutor_role.name})
        self.user.refresh_from_db()

        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(self.user.current_active_role, self.tutor_role)
        self.assertTemplateUsed("tutor_page.html")
