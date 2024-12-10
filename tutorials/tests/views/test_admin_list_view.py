from django.urls import reverse
from tutorials.models import Lesson, ProgrammingLanguage, Subject
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import AdminMixin, StudentMixin, TutorMixin

class AdminListTestMixin(RoleSetupTest, AdminMixin):
    """Mixin for testing admin list views."""
    list_type = None  
    
    def setUp(self):
        self.setup_admin()
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)

    def test_url_resolves_correctly(self):
        """Test reverse resolves to the expected URL."""
        url = reverse('admin_list', kwargs={'list_type': self.list_type})
        self.assertEqual(url, f'/admin_list/{self.list_type}/')

    def test_view_renders(self):
        """Test the view renders successfully with the expected template."""
        url = reverse('admin_list', kwargs={'list_type': self.list_type})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_list.html')

    def test_page_content(self):
        """Test page content is rendered correctly."""
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


class AdminStudentListTestCase(AdminListTestMixin, StudentMixin):
    list_type = 'students'

    def setUp(self):
        super().setUp()
        self.setup_student()

class AdminTutorListTestCase(AdminListTestMixin, TutorMixin):
    list_type = 'tutors'

    def setUp(self):
        super().setUp()
        self.setup_tutor()


class AdminBookingsListTestCase(AdminListTestMixin, StudentMixin, TutorMixin):
    list_type = 'bookings'

    def setUp(self):
        super().setUp()
        self.setup_tutor()
        self.setup_student()
        
        self.language = ProgrammingLanguage.objects.create(name="Python")

        self.subject = Subject.objects.create(
            name="Flask", 
            language=self.language, 
            description="Web development in Flask"
        )
        
        self.booking = Lesson.objects.create(
            student=self.student_user, 
            tutor=self.tutor_user, 
            language=self.language,
            subject=self.subject,
            lesson_datetime="2024-12-12 10:00:00",
        )






