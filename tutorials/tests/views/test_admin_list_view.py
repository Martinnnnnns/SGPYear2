'''
from django.test import TestCase
from django.urls import reverse

from tutorials.models import User

class AdminListTestMixin:
    """Mixin for testing admin list views."""
    url_name = None  
    
    def setUp(self):
        self.url = reverse(self.url_name)
        self.admin_user = User.objects.create_user(email="bobby@gmail.com", first_name="bob", last_name="bobby", username='@admin', password='Password123', role='admin')

    def test_url_resolves_correctly(self):
        """Test that reverse resolves to the expected URL."""
        self.assertEqual(self.url, f'/{self.url_name}/')  # Adjust URL structure as needed

    def test_view_renders(self):
        """Test that the view renders successfully with the expected template."""
        self.client.login(username='@admin', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.url_name}.html')

class AdminStudentListTestCase(AdminListTestMixin, TestCase):
    url_name = 'admin_list/students/'


class AdminTutorListTestCase(AdminListTestMixin, TestCase):
    url_name = 'admin_list/tutors/'


class AdminBookingsListTestCase(AdminListTestMixin, TestCase):
    url_name = 'admin_list/bookings/'

'''

from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Lesson, ProgrammingLanguage, Subject
from django.core.paginator import Paginator


class AdminListTestMixin:
    """Mixin for testing admin list views."""
    list_type = None  # Set dynamically in each test class
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="bobby@gmail.com", 
            first_name="bob", 
            last_name="bobby", 
            username='@admin', 
            password='Password123', 
            role='admin'
        )
        self.client.login(username='@admin', password='Password123')

    def test_url_resolves_correctly(self):
        """Test that reverse resolves to the expected URL."""
        url = reverse('admin_list', kwargs={'list_type': self.list_type})
        self.assertEqual(url, f'/admin_list/{self.list_type}/')

    def test_view_renders(self):
        """Test that the view renders successfully with the expected template."""
        url = reverse('admin_list', kwargs={'list_type': self.list_type})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_list.html')

    def test_page_content(self):
        """Test that page content is rendered correctly."""
        url = reverse('admin_list', kwargs={'list_type': self.list_type})
        response = self.client.get(url)

        # Test that table headers match the list type
        if self.list_type == 'student':
            self.assertContains(response, "Username")
            self.assertContains(response, "Name")
            self.assertContains(response, "Email")
        elif self.list_type == 'tutor':
            self.assertContains(response, "Programming Language")
            self.assertContains(response, "Subject")
        elif self.list_type == 'booking':
            self.assertContains(response, "Student")
            self.assertContains(response, "Tutor")
            self.assertContains(response, "Language")
            self.assertContains(response, "Subject")
            self.assertContains(response, "Date")


class AdminStudentListTestCase(AdminListTestMixin, TestCase):
    list_type = 'students'

    def setUp(self):
        super().setUp()
        # Add students for the test
        self.student = User.objects.create_user(
            email="student@gmail.com", 
            first_name="John", 
            last_name="Doe", 
            username='@student', 
            password='Password123', 
            role='student'
        )


class AdminTutorListTestCase(AdminListTestMixin, TestCase):
    list_type = 'tutors'

    def setUp(self):
        super().setUp()
        # Add tutors for the test
        self.tutor = User.objects.create_user(
            email="tutor@gmail.com", 
            first_name="Alice", 
            last_name="Smith", 
            username='@tutor', 
            password='Password123', 
            role='tutor'
        )


class AdminBookingsListTestCase(AdminListTestMixin, TestCase):
    list_type = 'bookings'

    def setUp(self):
        super().setUp()
        # Add bookings for the test
        self.student = User.objects.create_user(
            email="student@gmail.com", 
            first_name="John", 
            last_name="Doe", 
            username='@student', 
            password='Password123', 
            role='student'
        )
        self.tutor = User.objects.create_user(
            email="tutor@gmail.com", 
            first_name="Alice", 
            last_name="Smith", 
            username='@tutor', 
            password='Password123', 
            role='tutor'
        )
        
        # Create a programming language instance
        self.language = ProgrammingLanguage.objects.create(name="Python")

        # Create a subject instance related to the language
        self.subject = Subject.objects.create(
            name="Flask", 
            language=self.language, 
            description="Web development in Flask"
        )
        
        # Create a booking
        self.booking = Lesson.objects.create(
            student=self.student, 
            tutor=self.tutor, 
            language=self.language,
            subject=self.subject,
            lesson_datetime="2024-12-12 10:00:00",
        )






