from django.urls import reverse
from django.test import TestCase
from django.utils.timezone import now
from tutorials.models import User, Invoice, LessonRequest, ProgrammingLanguage, Subject
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin

class StudentViewsTests(RoleSetupTest, StudentMixin):
    def setUp(self):
        self.setup_student()
        self.invoice_url = reverse('student_invoices')
        self.pending_requests_url = reverse('student_pending_requests')

        # Test data
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Intro to Python", language=self.language)
        Invoice.objects.create(student=self.student_user, amount=100.0, status='paid')
        LessonRequest.objects.create(
            user=self.student_user,
            language=self.language,
            subject=self.subject,
            start_datetime=now(),
            end_datetime=now(),
            status='pending'
        )

    def test_student_invoices_view(self):
        """Test the student invoices view."""
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(self.invoice_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_invoices.html')
        self.assertEqual(response.context['invoices'].count(), 1)

    def test_student_pending_requests_view(self):
        """Test the student pending requests view."""
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(self.pending_requests_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_pending_requests.html')
        self.assertEqual(response.context['lesson_requests'].count(), 1)
