from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from tutorials.models import User, TutorAvailability
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin, TutorMixin
from tutorials.views import DeleteAvailabilityView, DeleteAllAvailabilityView  # Add the imports

class TestDeleteAvailability(RoleSetupTest, StudentMixin, TutorMixin):
    def setUp(self):
        self.setup_tutor()
        self.setup_student()
        
        self.other_tutor_user = User.objects.create_user(
            username='@tutor2',
            first_name='Other',
            last_name='Tutor',
            email='other@test.com',
            password='Password123',
        )
        self.other_tutor_user.roles.set([self.tutor_role])
        self.other_tutor_user.current_active_role = self.tutor_role
        self.other_tutor_user.save()
        
        self.tomorrow = timezone.now().date() + timedelta(days=1)
        self.availability = TutorAvailability.objects.create(
            tutor=self.tutor_user,
            date=self.tomorrow,
            start_time='10:00',
            end_time='11:00'
        )

    def test_delete_availability_requires_login(self):
        """Test that delete availability requires login"""
        url = reverse('delete_availability', args=[self.availability.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in/'))
        self.assertEqual(TutorAvailability.objects.count(), 1)

    def test_delete_availability_requires_tutor_role(self):
        """Test that only tutors can delete availability"""
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        url = reverse('delete_availability', args=[self.availability.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(TutorAvailability.objects.count(), 1)

    def test_delete_own_availability_successful(self):
        """Test tutor can delete their own availability slot"""
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
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
        self.client.login(username=self.other_tutor_user.username, password='Password123')
        url = reverse('delete_availability', args=[self.availability.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(TutorAvailability.objects.count(), 1)

    def test_delete_nonexistent_availability(self):
        """Test attempting to delete non-existent availability slot"""
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        url = reverse('delete_availability', args=[99999])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(TutorAvailability.objects.count(), 1)

    def test_delete_availability_get_request(self):
        """Test that GET request to delete availability is handled"""
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        url = reverse('delete_availability', args=[self.availability.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('schedule_sessions'))
        self.assertEqual(TutorAvailability.objects.count(), 1)

    def test_delete_all_availability_requires_login(self):
        """Test that delete all availability requires login"""
        url = reverse('delete_all_availability')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in/'))
        self.assertEqual(TutorAvailability.objects.count(), 1)

    def test_delete_all_availability_requires_tutor_role(self):
        """Test that only tutors can delete all availability"""
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        url = reverse('delete_all_availability')
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(TutorAvailability.objects.count(), 1)

    def test_delete_all_availability_successful(self):
        """Test tutor can delete all their availability slots"""
        TutorAvailability.objects.create(
            tutor=self.tutor_user,
            date=self.tomorrow + timedelta(days=1),
            start_time='14:00',
            end_time='15:00'
        )
        
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        url = reverse('delete_all_availability')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('schedule_sessions'))
        self.assertEqual(TutorAvailability.objects.filter(tutor=self.tutor_user).count(), 0)
        self.assertEqual(
            self.client.session.get('success_message'),
            "All availability slots deleted successfully"
        )

    def test_delete_all_availability_only_deletes_own_slots(self):
        """Test delete all only removes the tutor's own slots"""
        other_slot = TutorAvailability.objects.create(
            tutor=self.other_tutor_user,
            date=self.tomorrow,
            start_time='12:00',
            end_time='13:00'
        )
        
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        url = reverse('delete_all_availability')
        response = self.client.post(url)
        
        self.assertTrue(TutorAvailability.objects.filter(id=other_slot.id).exists())
        self.assertEqual(TutorAvailability.objects.filter(tutor=self.tutor_user).count(), 0)

    def test_delete_all_availability_with_no_slots(self):
        """Test delete all when tutor has no availability slots"""
        self.availability.delete()
        
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        url = reverse('delete_all_availability')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('schedule_sessions'))
        self.assertEqual(
            self.client.session.get('success_message'),
            "All availability slots deleted successfully"
        )