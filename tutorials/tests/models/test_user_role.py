from django.test import TestCase
from tutorials.models import Role, User

class UserModelTest(TestCase):
    
    def setUp(self):
        """Set up initial data for testing."""
        self.role_student = Role.objects.create(name="student")
        self.role_tutor = Role.objects.create(name="tutor")
        self.role_admin = Role.objects.create(name="admin")
        self.user = User.objects.create_user(
            username='@john123',
            email='john@example.com',
            first_name='John',
            last_name='Doe'
        )
    
    def test_create_user_with_multiple_roles(self):
        """Test that a user can have multiple roles."""
        self.user.roles.add(self.role_student, self.role_tutor)
        self.assertIn(self.role_student, self.user.roles.all())
        self.assertIn(self.role_tutor, self.user.roles.all())
    
    def test_current_active_role_valid(self):
        """Test that the current active role is part of the assigned roles."""
        self.user.roles.add(self.role_student, self.role_tutor)
        self.user.current_active_role = self.role_student
        self.user.save()  
        self.assertEqual(self.user.current_active_role, self.role_student)
    
    def test_current_active_role_invalid(self):
        """Test that a ValueError is raised if the current active role is not part of the assigned roles."""
        self.user.roles.add(self.role_student, self.role_tutor)
        self.user.current_active_role = self.role_admin  # Not assigned to the user
        with self.assertRaises(ValueError):
            self.user.save()

    def test_user_str_method(self):
        """Test that the __str__ method returns the correct string representation."""
        self.user.roles.add(self.role_student, self.role_tutor)
        self.user.current_active_role = self.role_tutor
        self.assertEqual(
            str(self.user),
            "John Doe (student, tutor) - Active Role: tutor"
        )

