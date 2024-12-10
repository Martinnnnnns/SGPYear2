from django.urls import reverse
from django.core.exceptions import ValidationError
from tutorials.forms import AdminAddBookingForm
from tutorials.models import User, Lesson
from tutorials.models import ProgrammingLanguage, Subject
from datetime import datetime
from django.utils import timezone
from datetime import timedelta

from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import AdminMixin, StudentMixin, TutorMixin


class AddUserViewTests(RoleSetupTest, StudentMixin, AdminMixin, TutorMixin):
    def setUp(self):
        self.setup_admin()
        self.setup_student()
        self.setup_tutor()

        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)

    def test_post_add_student_view(self):
        """Test creating a student via POST."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)

        post_data = {
            'username': '@newstudent',  # Updated username
            'email': 'student@example.com',
            'password': 'securepassword123',
            'first_name': 'Student',
            'last_name': 'Test'
        }

        # URL to add user as student
        url = reverse('add_user', kwargs={'role': 'student'})
        response = self.client.post(url, post_data, follow=True)  

        # Check if the student is in the database with the correct role
        student = User.objects.filter(email='student@example.com').first()
        self.assertIsNotNone(student)
        self.assertEqual(student.current_active_role, 'student')  



    def test_post_add_tutor_view(self):
        """Test creating a tutor via POST."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)

        post_data = {
            'username': '@newtutor',  # Updated username
            'email': 'tutor@example.com',
            'password': 'securepassword123',
            'first_name': 'Tutor',
            'last_name': 'Test'
        }

        # URL to add user as tutor
        url = reverse('add_user', kwargs={'role': 'tutor'})
        response = self.client.post(url, post_data, follow=True)  

        # Check if the tutor is in the database with the correct role
        tutor = User.objects.filter(email='tutor@example.com').first()
        self.assertIsNotNone(tutor)
        self.assertEqual(tutor.current_active_role, 'tutor')  
    
    def test_post_add_booking_view(self):
        """Test creating a tutor via POST."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)

        post_data = {
            'student': self.student_user,
            'tutor': self.tutor_user,
            'language': self.language,
            'subject': self.subject,
            'lesson_datetime': timezone.now() + timedelta(days=1),
            'status': Lesson.STATUS_SCHEDULED
        }

        # URL to add user as tutor
        url = reverse('add_user', kwargs={'role': 'booking'})
        response = self.client.post(url, post_data, follow=True)  

        # Check if the tutor is in the database with the correct role
        lesson = Lesson.objects.filter(student=self.student_user, tutor=self.tutor_user)

        # Check if a lesson exists
        self.assertIsNotNone(lesson)