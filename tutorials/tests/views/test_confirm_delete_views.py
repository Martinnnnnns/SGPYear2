from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from tutorials.models import User, TutorAvailability
from django.contrib.messages import get_messages

class TestConfirmDeleteViews(TestCase):
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
        self.test_slot = TutorAvailability.objects.create(
            tutor=self.tutor,
            date=self.tomorrow,
            start_time='10:00',
            end_time='11:00'
        )

    def test_confirm_delete_requires_login(self):
        """Test that the confirm delete view requires login"""
        url = reverse('confirm_delete_availability', args=[self.test_slot.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        expected_url = f"/log_in/?next={url}"
        self.assertEqual(response.url, expected_url)
    def test_student_cannot_delete_slot(self):
        """Test that student cannot delete slots"""
        self.client.login(username='@student1', password='Password123')
        url = reverse('confirm_delete_availability', args=[self.test_slot.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/access_denied')

    def test_tutor_can_access_delete_confirmation(self):
        """Test that tutor can access delete confirmation page"""
        self.client.login(username='@tutor1', password='Password123')
        url = reverse('confirm_delete_availability', args=[self.test_slot.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirm_delete_availability.html')

    def test_confirm_delete_post_request(self):
        """Test that POST request deletes the slot"""
        self.client.login(username='@tutor1', password='Password123')
        url = reverse('confirm_delete_availability', args=[self.test_slot.id])
        response = self.client.post(url)
        messages = list(get_messages(response.wsgi_request))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('schedule_sessions'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Availability slot deleted successfully.")
        self.assertEqual(TutorAvailability.objects.count(), 0)

    def test_cannot_delete_other_tutor_slot(self):
        """Test that tutor cannot delete another tutor's slot"""
        self.client.login(username='@tutor2', password='Password123')
        url = reverse('confirm_delete_availability', args=[self.test_slot.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_tutor_can_access_delete_all_confirmation(self):
        """Test that tutor can access delete all confirmation page"""
        self.client.login(username='@tutor1', password='Password123')
        url = reverse('confirm_delete_all_availabilities')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirm_delete_all_availabilities.html')

    def test_invalid_role_delete_all(self):
        """Test that invalid role cannot access delete all confirmation"""
        self.client.login(username='@student1', password='Password123')
        url = reverse('confirm_delete_all_availabilities')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/access_denied')

    def test_delete_all_no_slots_exists(self):
        """Test response when no slots exist to delete"""
        TutorAvailability.objects.all().delete()
        
        self.client.login(username='@tutor1', password='Password123')
        url = reverse('confirm_delete_all_availabilities')
        response = self.client.get(url)
        messages = list(get_messages(response.wsgi_request))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('schedule_sessions'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "There are no slots to delete.")

    def test_delete_all_only_deletes_own_slots(self):
        """Test that delete all only removes the tutor's own slots"""
        other_slot = TutorAvailability.objects.create(
            tutor=self.other_tutor,
            date=self.tomorrow,
            start_time='12:00',
            end_time='13:00'
        )
        
        self.client.login(username='@tutor1', password='Password123')
        url = reverse('confirm_delete_all_availabilities')
        response = self.client.post(url)
        
        self.assertTrue(TutorAvailability.objects.filter(id=other_slot.id).exists())
        self.assertEqual(TutorAvailability.objects.filter(tutor=self.tutor).count(), 0)

    def test_confirm_delete_all_post_request(self):
        """Test that POST request deletes all slots"""
        # Create additional slots
        TutorAvailability.objects.create(
            tutor=self.tutor,
            date=self.tomorrow + timedelta(days=1),
            start_time='14:00',
            end_time='15:00'
        )
        
        self.client.login(username='@tutor1', password='Password123')
        url = reverse('confirm_delete_all_availabilities')
        response = self.client.post(url)
        messages = list(get_messages(response.wsgi_request))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('schedule_sessions'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "All availability slots deleted successfully.")
        self.assertEqual(TutorAvailability.objects.filter(tutor=self.tutor).count(), 0)

    def test_confirm_delete_invalid_slot_id(self):
        """Test attempting to delete non-existent slot"""
        self.client.login(username='@tutor1', password='Password123')
        url = reverse('confirm_delete_availability', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)