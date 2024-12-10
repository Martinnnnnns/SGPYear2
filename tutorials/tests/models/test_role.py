from django.test import TestCase
from tutorials.models import Role

class RoleModelTest(TestCase):
    
    def setUp(self):
        """Set up any initial data needed for the tests."""
        self.role_name = "student"
    
    def test_create_role(self):
        """Test that a role can be created successfully."""
        role = Role.objects.create(name=self.role_name)
        self.assertEqual(role.name, self.role_name)
        self.assertTrue(isinstance(role, Role))
    
    def test_role_name_unique(self):
        """Test that duplicate role names are not allowed."""
        Role.objects.create(name=self.role_name)
        with self.assertRaises(Exception):  # Expecting a unique constraint error
            Role.objects.create(name=self.role_name)
    
    def test_str_method(self):
        """Test that the __str__ method returns the role name."""
        role = Role.objects.create(name=self.role_name)
        self.assertEqual(str(role), self.role_name)
