from django.urls import reverse
from django.test import TestCase
from django.test import TestCase
from django.core.exceptions import ValidationError
from tutorials.forms import AdminAddBookingForm
from tutorials.models import User, Lesson
from tutorials.models import ProgrammingLanguage, Subject
from datetime import datetime
from django.utils import timezone
from datetime import timedelta


class AddUserViewTests(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            email='admin@example.com',
            role='admin'
        )
        
        self.student = User.objects.create_user(
            username="student",
            password="Password123",
            email="student@example.com",
            role="student"
        )
        self.tutor = User.objects.create_user(
            username="tutor",
            password="Password123",
            email="tutor@example.com",
            role="tutor"
        )

        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)

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
    
    
    def test_post_add_booking_view(self):
        """Test creating a tutor via POST."""
        self.client.login(username='admin', password='adminpass')  # Log in as admin

        # POST data (including role)
        post_data = {
            'student': self.student,
            'tutor': self.tutor,
            'language': self.language,
            'subject': self.subject,
            'lesson_datetime': timezone.now() + timedelta(days=1),
            'status': Lesson.STATUS_SCHEDULED
        }

        # URL to add user as tutor
        url = reverse('add_user', kwargs={'role': 'booking'})
        response = self.client.post(url, post_data, follow=True)  # Use follow=True to follow the redirect

        # Check if the tutor is in the database with the correct role
        
        lesson = Lesson.objects.filter(student=self.student, tutor=self.tutor)

        # Check if a lesson exists
        self.assertIsNotNone(lesson)