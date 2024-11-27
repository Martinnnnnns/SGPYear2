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
        # Create slots in random order
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
        # Verify ordering by date, then start_time
        self.assertEqual(slots[0].date, self.tomorrow)
        self.assertEqual(slots[0].start_time.strftime('%H:%M'), '10:00')
        self.assertEqual(slots[1].date, self.tomorrow)
        self.assertEqual(slots[1].start_time.strftime('%H:%M'), '11:00')