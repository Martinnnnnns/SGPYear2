from django.test import TestCase
from tutorials.models import Role
from tutorials.constants import UserRoles

class RoleSetupTest(TestCase):
    """Base test to create roles for the whole class once."""
    PASSWORD = "Password123"  #Shared password for all test users
    
    @classmethod
    def setUpTestData(cls):
        """Create shared roles once for the entire test class"""
        cls.admin_role = Role.objects.create(name=UserRoles.ADMIN)
        cls.tutor_role = Role.objects.create(name=UserRoles.TUTOR)
        cls.student_role = Role.objects.create(name=UserRoles.STUDENT)

    def setUp(self):
        #Any additional setup shared across all subclasses can go here
        pass
