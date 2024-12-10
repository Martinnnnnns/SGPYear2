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
            lesson_datetime=timezone.now()  # Providing a default datetime
        )
        self.lesson2 = Lesson.objects.create(
            student=self.student_user,
            tutor=self.tutor_user,
            language=self.language,
            lesson_datetime=timezone.now()  # Providing a default datetime
        )  # No subject (general lesson)

        # Create some invoices
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

    def test_lessons_displayed_on_dashboard(self):
        """Ensure lessons assigned to the user are displayed on the dashboard."""
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, self.subject.name)
        self.assertContains(response, self.language.name)

    def test_invoices_displayed_on_dashboard(self):
        """Ensure invoices assigned to the user are displayed on the dashboard."""
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, f'${self.invoice1.amount}')
        self.assertContains(response, f'${self.invoice2.amount}')
        self.assertContains(response, 'Paid')
        self.assertContains(response, 'Unpaid')

    def test_lesson_requests_displayed_on_dashboard(self):
        """Ensure lesson requests assigned to the user are displayed on the dashboard."""
        response = self.client.get(reverse('dashboard'))
        
        # Check that lesson requests are displayed correctly
        self.assertEqual(response.context["lesson_requests"].count(), 0)
        self.assertContains(response, self.lesson_request.subject.name)
        self.assertContains(response, self.language.name)

    def test_no_lesson_requests_displayed_on_dashboard(self):
        """Ensure the dashboard doesn't display lesson requests when there are none."""
        LessonRequest.objects.all().delete()
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'pending')
