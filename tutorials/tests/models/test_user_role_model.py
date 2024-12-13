from django.test import TestCase
from tutorials.models import Role, User

class UserModelTest(TestCase):
    
    def setUp(self):
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
        self.user.roles.add(self.role_student, self.role_tutor)
        self.assertIn(self.role_student, self.user.roles.all())
        self.assertIn(self.role_tutor, self.user.roles.all())
    
    def test_current_active_role_valid(self):
        self.user.roles.add(self.role_student, self.role_tutor)
        self.user.current_active_role = self.role_student
        self.user.save()  
        self.assertEqual(self.user.current_active_role, self.role_student)
    
    def test_current_active_role_invalid(self):
        self.user.roles.add(self.role_student, self.role_tutor)
        self.user.current_active_role = self.role_admin 
        with self.assertRaises(ValueError):
            self.user.save()

    def test_user_str_method(self):
        self.user.roles.add(self.role_student, self.role_tutor)
        self.user.current_active_role = self.role_tutor
        self.assertEqual(
            str(self.user),
            "John Doe (student, tutor) - Active Role: tutor"
        )

