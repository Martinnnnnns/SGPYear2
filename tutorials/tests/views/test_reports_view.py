from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from tutorials.models import User, Lesson, ProgrammingLanguage
from datetime import timedelta
import io
from reportlab.pdfgen import canvas
from django.http import HttpResponse

class ReportsViewTests(TestCase):
    def setUp(self):
        self.url = reverse('reports')
        self.tutor_user = User.objects.create_user(
            username='@tutor_user',
            password='testpassword123',
            email='tutor_user@example.com',
            role='tutor',
            first_name='Test',
            last_name='Tutor'
        )
        self.admin_user = User.objects.create_user(
            username='@admin_user',
            password='testpassword123',
            email='admin_user@example.com',
            role='admin'
        )
        self.student_user = User.objects.create_user(
            username='@student_user',
            password='testpassword123',
            email='student_user@example.com',
            role='student',
            first_name='Test',
            last_name='Student'
        )

        self.programming_language = ProgrammingLanguage.objects.create(
            name='Python'
        )

        self.today = now()
        self.lesson_today = Lesson.objects.create(
            tutor=self.tutor_user,
            student=self.student_user,
            lesson_datetime=self.today,
            language=self.programming_language
        )
        self.lesson_week_ago = Lesson.objects.create(
            tutor=self.tutor_user,
            student=self.student_user,
            lesson_datetime=self.today - timedelta(days=5),
            language=self.programming_language
        )
        self.lesson_month_ago = Lesson.objects.create(
            tutor=self.tutor_user,
            student=self.student_user,
            lesson_datetime=self.today - timedelta(days=20),
            language=self.programming_language
        )

    def test_reports_url(self):
        self.assertEqual(self.url, reverse('reports'))

    def test_tutor_access_reports(self):
        """Test that a tutor can access the reports page."""
        self.client.login(username='@tutor_user', password='testpassword123')
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports.html')

    def test_admin_access_reports(self):
        """Test that an admin can access the reports page."""
        self.client.login(username='@admin_user', password='testpassword123')
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports.html')

    def test_non_authorised_user_redirect(self):
        """Test that a non-authorised user is redirected to their home page."""
        self.client.login(username='@student_user', password='testpassword123')
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 302)

    def test_login_required_reports(self):
        """Test that an unauthenticated user is redirected to the login page."""
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in/'))

    def test_generate_report_unauthorized_user(self):
        """Test that non-tutor users cannot generate reports."""
        self.client.login(username='@student_user', password='testpassword123')
        response = self.client.get(reverse('generate_report', kwargs={'time_period': '7days'}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content.decode(), "You are not authorized to access this resource.")

    def test_generate_report_invalid_time_period(self):
        """Test handling of invalid time period."""
        self.client.login(username='@tutor_user', password='testpassword123')
        response = self.client.get(reverse('generate_report', kwargs={'time_period': 'invalid'}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Invalid time period.")

    def test_generate_report_7days(self):
        """Test generating a 7-day report."""
        self.client.login(username='@tutor_user', password='testpassword123')
        response = self.client.get(reverse('generate_report', kwargs={'time_period': '7days'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="tutor_report_7days.pdf"'
        )

    def test_generate_report_month(self):
        """Test generating a monthly report."""
        self.client.login(username='@tutor_user', password='testpassword123')
        response = self.client.get(reverse('generate_report', kwargs={'time_period': 'month'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="tutor_report_month.pdf"'
        )

    def test_generate_report_all(self):
        """Test generating a report for all time."""
        self.client.login(username='@tutor_user', password='testpassword123')
        response = self.client.get(reverse('generate_report', kwargs={'time_period': 'all'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="tutor_report_all.pdf"'
        )

    def test_generate_report_content(self):
        """Test the content of generated PDF report."""
        self.client.login(username='@tutor_user', password='testpassword123')
        response = self.client.get(reverse('generate_report', kwargs={'time_period': 'all'}))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

        self.assertTrue(len(response.content) > 0)

    def test_generate_report_many_lessons(self):
        """Test generating a report with many lessons (testing pagination)."""
        for i in range(30):
            Lesson.objects.create(
                tutor=self.tutor_user,
                student=self.student_user,
                lesson_datetime=self.today - timedelta(days=i),
                language=self.programming_language
            )

        self.client.login(username='@tutor_user', password='testpassword123')
        response = self.client.get(reverse('generate_report', kwargs={'time_period': 'all'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def tearDown(self):
        User.objects.all().delete()
        Lesson.objects.all().delete()
        ProgrammingLanguage.objects.all().delete()