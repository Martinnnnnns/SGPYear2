from django.test import TestCase
from tutorials.models import Role

class RoleModelTest(TestCase):
    
    def setUp(self):
        self.role_name = "student"
    
    def test_create_role(self):
        role = Role.objects.create(name=self.role_name)
        self.assertEqual(role.name, self.role_name)
        self.assertTrue(isinstance(role, Role))
    
    def test_role_name_unique(self):
        Role.objects.create(name=self.role_name)
        with self.assertRaises(Exception):  
            Role.objects.create(name=self.role_name)
    
    def test_str_method(self):
        role = Role.objects.create(name=self.role_name)
        self.assertEqual(str(role), self.role_name)
