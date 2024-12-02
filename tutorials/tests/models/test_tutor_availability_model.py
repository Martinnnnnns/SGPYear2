from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from tutorials.models import User, TutorAvailability

class TestTutorAvailability(TestCase):
    def setUp(self):
        self.tutor = User.objects.create_user(
            username='@tutor1',
            first_name='Test',
            last_name='Tutor',
            email='tutor@test.com',
            password='Password123',
            role='tutor'
        )
        self.tomorrow = timezone.now().date() + timedelta(days=1)

    def test_create_availability(self):
        availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            date=self.tomorrow,
            start_time='10:00',
            end_time='11:00'
        )
        self.assertEqual(TutorAvailability.objects.count(), 1)
        self.assertEqual(availability.tutor, self.tutor)

    def test_ordering(self):
        TutorAvailability.objects.create(
            tutor=self.tutor,
            date=self.tomorrow + timedelta(days=1),
            start_time='10:00',
            end_time='11:00'
        )
        TutorAvailability.objects.create(
            tutor=self.tutor,
            date=self.tomorrow,
            start_time='11:00',
            end_time='12:00'
        )
        TutorAvailability.objects.create(
            tutor=self.tutor,
            date=self.tomorrow,
            start_time='10:00',
            end_time='11:00'
        )

        slots = TutorAvailability.objects.all()
        self.assertEqual(slots[0].date, self.tomorrow)
        self.assertEqual(slots[0].start_time.strftime('%H:%M'), '10:00')
        self.assertEqual(slots[1].date, self.tomorrow)
        self.assertEqual(slots[1].start_time.strftime('%H:%M'), '11:00')

    def test_recurring_weekly_creation(self):
        next_week = self.tomorrow + timedelta(days=7)
        availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            date=self.tomorrow,
            start_time='10:00',
            end_time='11:00',
            recurrence='weekly',
            end_recurrence_date=next_week
        )
        self.assertEqual(availability.recurrence, 'weekly')
        self.assertEqual(availability.end_recurrence_date, next_week)

    def test_recurring_biweekly_creation(self):
        two_weeks_later = self.tomorrow + timedelta(days=14)
        availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            date=self.tomorrow,
            start_time='10:00',
            end_time='11:00',
            recurrence='biweekly',
            end_recurrence_date=two_weeks_later
        )
        self.assertEqual(availability.recurrence, 'biweekly')
        self.assertEqual(availability.end_recurrence_date, two_weeks_later)