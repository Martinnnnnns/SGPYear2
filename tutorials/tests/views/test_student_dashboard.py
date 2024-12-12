from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from tutorials.models import Lesson, Invoice, Subject, ProgrammingLanguage, LessonRequest
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin, TutorMixin

User = get_user_model()

class StudentDashboardViewTest(RoleSetupTest, StudentMixin, TutorMixin):
    def setUp(self):
        self.setup_student()
        self.student_user.first_name = "student"
        self.student_user.save()
        self.setup_tutor()

        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        self.language = ProgrammingLanguage.objects.create(name="Python")

        self.subject = Subject.objects.create(
            name='Mathematics',
            language=self.language
        )

        self.lesson1 = Lesson.objects.create(
            student=self.student_user,
            tutor=self.tutor_user,  
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() 
        )
        self.lesson2 = Lesson.objects.create(
            student=self.student_user,
            tutor=self.tutor_user,
            language=self.language,
            lesson_datetime=timezone.now() 
        ) 

        self.invoice1 = Invoice.objects.create(
            amount=100,
            date='2024-11-15',
            student=self.student_user,
            status='paid'
        )
        self.invoice2 = Invoice.objects.create(
            amount=150,
            date='2024-11-16',
            student=self.student_user,
            status='unpaid'
        )

        self.lesson_request = LessonRequest(
            user=self.student_user,
            start_datetime=timezone.now() ,
            end_datetime=timezone.now() + timezone.timedelta(minutes=45),
            language=self.language,
            subject=self.subject
        )

    def test_dashboard_renders_correct_template(self):
        """Ensure the dashboard view uses the correct template."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_dashboard.html')

    def test_correct_name_is_rendered_on_dashboard(self):
        """Ensure right name is displayed on the dashboard."""
        response = self.client.get(reverse('dashboard'))       
        self.assertContains(response, self.student_user.first_name)

    def test_dashboard_options_displayed(self):
        """Make sure the main 6 menu options are present."""
        response = self.client.get(reverse("dashboard"))
        for title in ["Calendar", "Request Lesson", "Invoices", "Pending Requests",
                      "Profile", "Support"]:
            self.assertContains(response, title)
