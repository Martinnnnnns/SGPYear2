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

    def test_get_not_authenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

    def test_student_cannot_access_page(self):
        """Test that students are redirected away from the scheduling page"""
        self.client.login(username='@student1', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')  

    def test_add_availability_slot(self):
        """Test adding a single availability slot"""
        self.client.login(username='@tutor1', password='Password123')
        data = {
            'date': self.tomorrow,
            'start_time': '10:00',
            'end_time': '11:00',
            'recurrence': 'none',
            'end_recurrence_date': ''
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TutorAvailability.objects.count(), 1)
        
        # Verify slot details
        slot = TutorAvailability.objects.first()
        self.assertEqual(slot.tutor, self.tutor)
        self.assertEqual(slot.start_time.strftime('%H:%M'), '10:00')
        self.assertEqual(slot.end_time.strftime('%H:%M'), '11:00')

    def test_add_weekly_recurring_availability(self):
        """Test adding weekly recurring availability slots"""
        self.client.login(username='@tutor1', password='Password123')
        next_week = self.tomorrow + timedelta(days=7)
        data = {
            'date': self.tomorrow,
            'start_time': '10:00',
            'end_time': '11:00',
            'recurrence': 'weekly',
            'end_recurrence_date': next_week
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TutorAvailability.objects.count(), 2)

    def test_add_biweekly_recurring_availability(self):
        """Test adding biweekly recurring availability slots"""
        self.client.login(username='@tutor1', password='Password123')
        four_weeks_later = self.tomorrow + timedelta(days=28)
        data = {
            'date': self.tomorrow,
            'start_time': '10:00',
            'end_time': '11:00',
            'recurrence': 'biweekly',
            'end_recurrence_date': four_weeks_later
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TutorAvailability.objects.count(), 3)

    def test_calendar_navigation(self):
        """Test navigating between different months in the calendar"""
        self.client.login(username='@tutor1', password='Password123')
        next_month = timezone.now() + timedelta(days=32)
        response = self.client.get(f"{self.url}?month={next_month.month}&year={next_month.year}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, next_month.strftime('%B %Y'))

    def test_context_data(self):
        """Test that all required context data is present"""
        self.client.login(username='@tutor1', password='Password123')
        response = self.client.get(self.url)
        self.assertIn('calendar', response.context)
        self.assertIn('month_name', response.context)
        self.assertIn('year', response.context)
        self.assertIn('hours_range', response.context)
        self.assertIn('form', response.context)