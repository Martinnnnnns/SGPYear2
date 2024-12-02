from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from tutorials.forms import TutorAvailabilityForm
from tutorials.models import User

class TestTutorAvailabilityForm(TestCase):
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

    def test_valid_availability_slot(self):
        form_data = {
            'date': self.tomorrow,
            'start_time': '10:00',
            'end_time': '11:00'
        }
        form = TutorAvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertTrue(form.is_valid())

    def test_past_date_invalid(self):
        yesterday = timezone.now().date() - timedelta(days=1)
        form_data = {
            'date': yesterday,
            'start_time': '10:00',
            'end_time': '11:00'
        }
        form = TutorAvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_end_time_before_start_time_invalid(self):
        form_data = {
            'date': self.tomorrow,
            'start_time': '11:00',
            'end_time': '10:00'
        }
        form = TutorAvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn('end_time', form.errors)

    def test_overlapping_slots_invalid(self):
        form1_data = {
            'date': self.tomorrow,
            'start_time': '10:00',
            'end_time': '12:00'
        }
        form1 = TutorAvailabilityForm(data=form1_data, tutor=self.tutor)
        self.assertTrue(form1.is_valid())
        form1.save(commit=False).tutor = self.tutor
        form1.save()

        form2_data = {
            'date': self.tomorrow,
            'start_time': '11:00',
            'end_time': '13:00'
        }
        form2 = TutorAvailabilityForm(data=form2_data, tutor=self.tutor)
        self.assertFalse(form2.is_valid())
        self.assertIn('start_time', form2.errors)
        self.assertIn('end_time', form2.errors)

    def test_weekly_recurrence_valid(self):
        next_week = self.tomorrow + timedelta(days=7)
        form_data = {
            'date': self.tomorrow,
            'start_time': '10:00',
            'end_time': '11:00',
            'recurrence': 'weekly',
            'end_recurrence_date': next_week
        }
        form = TutorAvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertTrue(form.is_valid())

    def test_biweekly_recurrence_valid(self):
        two_weeks_later = self.tomorrow + timedelta(days=14)
        form_data = {
            'date': self.tomorrow,
            'start_time': '10:00',
            'end_time': '11:00',
            'recurrence': 'biweekly',
            'end_recurrence_date': two_weeks_later
        }
        form = TutorAvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertTrue(form.is_valid())

    def test_recurring_without_end_date_invalid(self):
        form_data = {
            'date': self.tomorrow,
            'start_time': '10:00',
            'end_time': '11:00',
            'recurrence': 'weekly',
            'end_recurrence_date': ''
        }
        form = TutorAvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn('end_recurrence_date', form.errors)

    def test_end_date_before_start_date_invalid(self):
        yesterday = self.tomorrow - timedelta(days=2)
        form_data = {
            'date': self.tomorrow,
            'start_time': '10:00',
            'end_time': '11:00',
            'recurrence': 'weekly',
            'end_recurrence_date': yesterday
        }
        form = TutorAvailabilityForm(data=form_data, tutor=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn('end_recurrence_date', form.errors)