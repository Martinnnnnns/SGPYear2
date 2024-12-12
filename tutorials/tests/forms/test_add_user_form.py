from django.test import TestCase
from django.core.exceptions import ValidationError
from tutorials.forms import AdminAddUserForm
from tutorials.models import User


class AdminAddUserFormTests(TestCase):

    def setUp(self):
        self.existing_user = User.objects.create_user(
            username='@existinguser',
            email='existing@example.com',
            password='password123',
            first_name='Existing',
            last_name='User'
        )

    def test_valid_form_data(self):
        """Test the form with valid data."""
        form_data = {
            'username': '@newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword123'
        }
        form = AdminAddUserForm(data=form_data)
        self.assertTrue(form.is_valid(), "The form should be valid with correct data.")
        
        user = form.save(commit=False)
        self.assertTrue(user.check_password('newpassword123'), "The password should be hashed.")

    def test_missing_required_fields(self):
        """Test the form with missing required fields."""
        form_data = {
            'username': '',
            'email': '',
            'first_name': '',
            'last_name': '',
            'password': ''
        }
        form = AdminAddUserForm(data=form_data)
        self.assertFalse(form.is_valid(), "The form should be invalid if required fields are missing.")
        self.assertIn('username', form.errors, "Username error should be present.")
        self.assertIn('email', form.errors, "Email error should be present.")
        self.assertIn('first_name', form.errors, "First name error should be present.")
        self.assertIn('last_name', form.errors, "Last name error should be present.")
        self.assertIn('password', form.errors, "Password error should be present.")

    def test_email_uniqueness_validation(self):
        """Test that the form raises an error for duplicate email."""
        form_data = {
            'username': '@anotheruser',
            'email': 'existing@example.com',  # Invalid duplicate email
            'first_name': 'Another',
            'last_name': 'User',
            'password': 'anotherpassword123'
        }
        form = AdminAddUserForm(data=form_data)
        self.assertFalse(form.is_valid(), "The form should be invalid with a duplicate email.")
        self.assertIn('email', form.errors, "Email uniqueness error should be present.")
        self.assertEqual(
            form.errors['email'][0],
            'User with this Email already exists.',
            "The error message for duplicate email should match."
        )

    def test_password_hashing_on_save(self):
        """Test that the password is hashed when saving."""
        form_data = {
            'username': '@secureuser',
            'email': 'secureuser@example.com',
            'first_name': 'Secure',
            'last_name': 'User',
            'password': 'securepassword123'
        }
        form = AdminAddUserForm(data=form_data)
        self.assertTrue(form.is_valid(), "The form should be valid with correct data.")
        
        user = form.save(commit=False)
        self.assertTrue(user.check_password('securepassword123'), "The saved password should be hashed.")
    
    def test_save_without_commit(self):
        """Test saving the form with commit=False."""
        form_data = {
            'username': '@testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword123'
        }
        form = AdminAddUserForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save(commit=False)
        self.assertFalse(user.pk, "The user should not be saved to the database yet.")
        self.assertTrue(user.check_password('testpassword123'), "The password should be hashed.")

    def test_invalid_email_format(self):
        """Test if an invalid email raises a validation error."""
        form_data = {
            'username': '@invaliduser',
            'email': 'invalidemail.com',  # Invalid email format
            'first_name': 'Invalid',
            'last_name': 'User',
            'password': 'validpassword123'
        }
        form = AdminAddUserForm(data=form_data)
        self.assertFalse(form.is_valid(), "The form should be invalid with an invalid email.")
        self.assertIn('email', form.errors, "Email error should be present.")
    