from django.urls import reverse
from django.test import TestCase
from tutorials.models import User
class AddUserViewTests(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            email='admin@example.com',
            role='admin'
        )

    def test_post_add_student_view(self):
        """Test creating a student via POST."""
        self.client.login(username='admin', password='adminpass')  # Log in as admin

        # POST data (including role)
        post_data = {
            'username': '@newstudent',  # Updated username
            'email': 'student@example.com',
            'password': 'securepassword123',
            'first_name': 'Student',
            'last_name': 'Test'
        }

        # URL to add user as student
        url = reverse('add_user', kwargs={'role': 'student'})
        response = self.client.post(url, post_data, follow=True)  # Use follow=True to follow the redirect

        # Check if the student is in the database with the correct role
        student = User.objects.filter(email='student@example.com').first()
        self.assertIsNotNone(student)
        self.assertEqual(student.role, 'student')  # Check if the role is correctly set



    def test_post_add_tutor_view(self):
        """Test creating a tutor via POST."""
        self.client.login(username='admin', password='adminpass')  # Log in as admin

        # POST data (including role)
        post_data = {
            'username': '@newtutor',  # Updated username
            'email': 'tutor@example.com',
            'password': 'securepassword123',
            'first_name': 'Tutor',
            'last_name': 'Test'
        }

        # URL to add user as tutor
        url = reverse('add_user', kwargs={'role': 'tutor'})
        response = self.client.post(url, post_data, follow=True)  # Use follow=True to follow the redirect

        # Check if the tutor is in the database with the correct role
        tutor = User.objects.filter(email='tutor@example.com').first()
        self.assertIsNotNone(tutor)
        self.assertEqual(tutor.role, 'tutor')  # Check if the role is correctly set
