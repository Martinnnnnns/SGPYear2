from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from tutorials.models import User, TutorAvailability
from django.contrib.messages import get_messages

class TestDeleteAvailability(TestCase):
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
        
        self.other_tutor = User.objects.create_user(
            username='@tutor2',
            first_name='Other',
            last_name='Tutor',
            email='other@test.com',
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
        self.availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            date=self.tomorrow,
            start_time='10:00',
            end_time='11:00'
        )

    def test_delete_availability_requires_login(self):
        """Test that delete availability requires login"""
        url = reverse('delete_availability', args=[self.availability.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        expected_url = f"/log_in/?next={url}"
        self.assertEqual(response.url, expected_url)
        self.assertEqual(TutorAvailability.objects.count(), 1)

    def test_delete_availability_requires_tutor_role(self):
        """Test that only tutors can delete availability"""
        self.client.login(username='@student1', password='Password123')
        url = reverse('delete_availability', args=[self.availability.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/access_denied')
        self.assertEqual(TutorAvailability.objects.count(), 1)

    def test_delete_own_availability_successful(self):
        """Test tutor can delete their own availability slot"""
        self.client.login(username='@tutor1', password='Password123')
        url = reverse('delete_availability', args=[self.availability.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('schedule_sessions'))
        self.assertEqual(TutorAvailability.objects.count(), 0)
        self.assertEqual(
            self.client.session.get('success_message'),
            "Availability slot deleted successfully"
        )

    def test_cannot_delete_other_tutor_availability(self):
        """Test tutor cannot delete another tutor's availability"""
        self.client.login(username='@tutor2', password='Password123')
        url = reverse('delete_availability', args=[self.availability.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(TutorAvailability.objects.count(), 1)

    def test_delete_availability_preserves_other_tutor_slots(self):
        """Test that deleting availability doesn't affect other tutors."""
        other_slot = TutorAvailability.objects.create(
            tutor=self.other_tutor,
            date=self.tomorrow,
            start_time='12:00',
            end_time='13:00'
        )
        self.client.login(username='@tutor1', password='Password123')
        url = reverse('delete_availability', args=[self.availability.id])
        response = self.client.post(url)
        self.assertTrue(TutorAvailability.objects.filter(id=other_slot.id).exists())
