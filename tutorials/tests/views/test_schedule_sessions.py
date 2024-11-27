from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from tutorials.models import User, TutorAvailability

class TestScheduleSessions(TestCase):
    def setUp(self):
        self.client = Client()
        self.tutor = User.objects.create_user(
            username='@tutor1',
            first_name='Test',
            last_name='Tutor',
            email='tutor@test.com',
            password='Password123',
            role='tutor'
        )
        self.student = User.objects.create_user(
            username='@student1',
            first_name='Test',
            last_name='Student',
            email='student@test.com',
            password='Password123',
            role='student'
        )
        self.tomorrow = timezone.now().date() + timedelta(days=1)
        self.url = reverse('schedule_sessions')

    def test_tutor_can_access_page(self):
        self.client.login(username='@tutor1', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule_sessions.html')

    def test_student_cannot_access_page(self):
        self.client.login(username='@student1', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_add_availability_slot(self):
        self.client.login(username='@tutor1', password='Password123')
        data = {
            'date': self.tomorrow,
            'start_time': '10:00',
            'end_time': '11:00'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TutorAvailability.objects.count(), 1)

    def test_calendar_navigation(self):
        self.client.login(username='@tutor1', password='Password123')
        next_month = timezone.now() + timedelta(days=32)
        response = self.client.get(f"{self.url}?month={next_month.month}&year={next_month.year}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, next_month.strftime('%B %Y'))

    def test_display_availability_slots(self):
        self.client.login(username='@tutor1', password='Password123')
        # Create a slot
        TutorAvailability.objects.create(
            tutor=self.tutor,
            date=self.tomorrow,
            start_time='10:00',
            end_time='11:00'
        )
        response = self.client.get(self.url)
        self.assertContains(response, '10:00')
        self.assertContains(response, '11:00')