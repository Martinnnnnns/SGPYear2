from django.test import TestCase
from django import forms  # Import forms here
from tutorials.forms import AdminUpdateUserForm
from tutorials.models import User, Role
from django.core.exceptions import ValidationError
from tutorials.constants import UserRoles

class AdminUpdateUserFormTests(TestCase):

    def setUp(self):
        """Set up test data."""
        #User to update
        self.existing_user = User.objects.create_user(
            username='@existing_user',
            email='existing@example.com',
            first_name='Existing',
            last_name='User',
            password='password123'
        )

        #Update data
        self.other_user = User.objects.create_user(
            username='@other_user',
            email='other@example.com',
            first_name='Other',
            last_name='User',
            password='password456'
        )

    def test_valid_update_form(self):
        """Test the form with valid data."""
        data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'username': '@existing_user_updated',
            'email': 'updated@example.com',
            'role': 'student',  
            'password': 'newpassword123'
        }
        form = AdminUpdateUserForm(instance=self.existing_user, data=data)

        self.assertTrue(form.is_valid(), "The form should be valid with unique email and valid data.")

        updated_user = form.save()
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.email, 'updated@example.com')
    
    def test_clean_add_current_active_role_to_roles(self):
        """Tests the current_active_role is added to roles if not there."""
        data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'username': '@existing_user_updated',
            'email': 'updated@example.com',
            'current_active_role': Role.objects.create(name=UserRoles.STUDENT),  
            'password': 'newpassword123'
        }
        
        form = AdminUpdateUserForm(instance=self.existing_user, data=data)
        self.assertTrue(form.is_valid())

        updated_user = form.save()

        self.assertIn(Role.objects.get(name=UserRoles.STUDENT), updated_user.roles.all(), "The student role should be added to the user's roles.")


    def test_clean_email_duplicate(self):
        """Test the clean_email method with a duplicate email."""
        data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'username': 'existing_user_updated',
            'email': 'other@example.com',  
            'role': 'student',
            'password': 'newpassword123'
        }
        form = AdminUpdateUserForm(instance=self.existing_user, data=data)

        self.assertFalse(form.is_valid(), "The form should not be valid with a duplicate email.")

        self.assertIn(
            'This email is already in use by another user.',
            form.errors['email'],
            "The form should raise a validation error for the duplicate email."
        )

    def test_password_field_is_empty_on_load(self):
        """Test that the password field is empty initially."""
        form = AdminUpdateUserForm(instance=self.existing_user)

        self.assertEqual(form.initial['password'], '', "The password field should be empty initially.")

    def test_password_field_is_password_input_widget(self):
        """Test that the password field is rendered as a password input."""
        form = AdminUpdateUserForm(instance=self.existing_user)

        self.assertIsInstance(
            form.fields['password'].widget, 
            forms.PasswordInput, 
            "The password field should use a PasswordInput widget."
        )