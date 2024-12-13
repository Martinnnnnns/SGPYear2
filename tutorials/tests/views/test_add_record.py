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
            'username': '@newstudent', 
            'email': 'student@example.com',
            'password': 'securepassword123',
            'first_name': 'Student',
            'last_name': 'Test'
        }

        url = reverse('add_record', kwargs={'role': 'student'})
        response = self.client.post(url, post_data, follow=True)  

        #Check database for student
        student = User.objects.filter(email='student@example.com').first()
        self.assertIsNotNone(student)
        self.assertEqual(student.current_active_role.name, 'student')  


    def test_post_add_tutor_view(self):
        """Test creating a tutor via POST."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)

        post_data = {
            'username': '@newtutor',  
            'email': 'tutor@example.com',
            'password': 'securepassword123',
            'first_name': 'Tutor',
            'last_name': 'Test'
        }

        url = reverse('add_record', kwargs={'role': 'tutor'})
        response = self.client.post(url, post_data, follow=True)  

        #Check database for tutor
        tutor = User.objects.filter(email='tutor@example.com').first()
        self.assertIsNotNone(tutor)
        self.assertEqual(tutor.current_active_role.name, 'tutor')  
    
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

        url = reverse('add_record', kwargs={'role': 'booking'})
        response = self.client.post(url, post_data, follow=True)  

        #Check database for booking
        lesson = Lesson.objects.filter(student=self.student_user, tutor=self.tutor_user)
        self.assertIsNotNone(lesson)
        
    def test_get_add_student_view(self):
        """Test correct form is displayed when adding a student."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)

        url = reverse('add_record', kwargs={'role': 'student'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'username')
        self.assertContains(response, 'email')
        
    def test_get_add_tutor_view(self):
        """Test correct form is displayed when adding a tutor."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)

        url = reverse('add_record', kwargs={'role': 'tutor'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_record.html')
        self.assertContains(response, 'username')
        self.assertContains(response, 'email')
        
    def test_get_add_booking_view(self):
        """Test correct form is displayed when adding a booking."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)

        url = reverse('add_record', kwargs={'role': 'booking'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_record.html')
        self.assertContains(response, 'student')
        self.assertContains(response, 'tutor')
        
        