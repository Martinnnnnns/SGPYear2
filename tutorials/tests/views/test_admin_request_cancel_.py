from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import (
    CancellationRequest,
    ChangeRequest,
    Lesson,
    ProgrammingLanguage,
    Subject,
    TutorAvailability
)
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class AdminReviewRequestsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpass',
            email='admin_user@example.com',
            role='admin'
        )
        self.student = User.objects.create_user(
            username='student_user',
            password='studentpass',
            email='student_user@example.com',
            role='student'
        )
        self.tutor = User.objects.create_user(
            username='tutor_user',
            password='tutorpass',
            email='tutor_user@example.com',
            role='tutor'
        )
        self.language = ProgrammingLanguage.objects.create(name='Ruby')
        self.subject = Subject.objects.create(name='Rails', language=self.language)
        self.lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() + timedelta(days=5),
            status=Lesson.STATUS_SCHEDULED
        )
        self.cancellation_request = CancellationRequest.objects.create(
            user=self.student,
            request_type=CancellationRequest.REQUEST_SINGLE,
            reason='Not needed anymore',
            status=CancellationRequest.STATUS_PENDING
        )
        self.cancellation_request.lessons.add(self.lesson)
        self.change_request = ChangeRequest.objects.create(
            user=self.student,
            new_datetime=timezone.now() + timedelta(days=6),
            reason='Need to reschedule',
            status=ChangeRequest.STATUS_PENDING
        )
        self.change_request.lessons.add(self.lesson)

    def test_admin_access_required(self):
        # Attempt to access without logging in
        response = self.client.get(reverse('admin_review_requests'))
        self.assertRedirects(response, '/log_in/?next=/admin-review/')
        # Login as non-admin
        self.client.login(username='student_user', password='studentpass')
        response = self.client.get(reverse('admin_review_requests'))
        self.assertEqual(response.status_code, 302)  # Assuming 403 Forbidden for unauthorized access

    def test_admin_can_view_pending_requests(self):
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.get(reverse('admin_review_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending Cancellation Requests')
        self.assertContains(response, 'Pending Change Requests')
        self.assertContains(response, self.cancellation_request.reason)
        self.assertContains(response, self.change_request.reason)

    def test_admin_approves_cancellation_request(self):
        self.client.login(username='admin_user', password='adminpass')
        url = reverse('admin_review_requests')
        data = {
            'request_id': self.cancellation_request.id,
            'request_type': 'cancellation',
            'action': 'approve',
            'admin_comment': 'Approved for cancellation.'
        }
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, "Cancellation request approved successfully.")

        # Refresh from DB
        self.cancellation_request.refresh_from_db()
        self.lesson.refresh_from_db()

        self.assertEqual(self.cancellation_request.status, CancellationRequest.STATUS_APPROVED)
        self.assertEqual(self.lesson.status, Lesson.STATUS_CANCELED)
        self.assertEqual(self.cancellation_request.admin_comment, 'Approved for cancellation.')

    def test_admin_rejects_cancellation_request(self):
        self.client.login(username='admin_user', password='adminpass')
        url = reverse('admin_review_requests')
        data = {
            'request_id': self.cancellation_request.id,
            'request_type': 'cancellation',
            'action': 'reject',
            'admin_comment': 'Cancellation not approved.'
        }
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, "Cancellation request rejected successfully.")

        # Refresh from DB
        self.cancellation_request.refresh_from_db()
        self.lesson.refresh_from_db()

        self.assertEqual(self.cancellation_request.status, CancellationRequest.STATUS_DENIED)
        self.assertEqual(self.lesson.status, Lesson.STATUS_SCHEDULED)  # Status should remain unchanged
        self.assertEqual(self.cancellation_request.admin_comment, 'Cancellation not approved.')

    def test_admin_approves_change_request_with_availability(self):
        # Set tutor availability
        TutorAvailability.objects.create(
            tutor=self.tutor,
            date=self.change_request.new_datetime.date(),
            start_time=(self.change_request.new_datetime - timedelta(hours=1)).time(),
            end_time=(self.change_request.new_datetime + timedelta(hours=1)).time()
        )
        self.client.login(username='admin_user', password='adminpass')
        url = reverse('admin_review_requests')
        data = {
            'request_id': self.change_request.id,
            'request_type': 'change',
            'action': 'approve',
            'admin_comment': 'Change request approved.'
        }
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, "Change request approved successfully.")

        # Refresh from DB
        self.change_request.refresh_from_db()
        self.lesson.refresh_from_db()

        self.assertEqual(self.change_request.status, ChangeRequest.STATUS_APPROVED)
        self.assertEqual(self.lesson.lesson_datetime, self.change_request.new_datetime)
        self.assertEqual(self.lesson.status, Lesson.STATUS_RESCHEDULED)
        self.assertEqual(self.change_request.admin_comment, 'Change request approved.')

    def test_admin_rejects_change_request(self):
        self.client.login(username='admin_user', password='adminpass')
        url = reverse('admin_review_requests')
        data = {
            'request_id': self.change_request.id,
            'request_type': 'change',
            'action': 'reject',
            'admin_comment': 'Change request denied.'
        }
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, "Change request rejected successfully.")

        # Refresh from DB
        self.change_request.refresh_from_db()
        self.lesson.refresh_from_db()

        self.assertEqual(self.change_request.status, ChangeRequest.STATUS_DENIED)
        self.assertEqual(self.lesson.lesson_datetime, self.lesson.lesson_datetime)  # No change
        self.assertEqual(self.lesson.status, Lesson.STATUS_SCHEDULED)  # No change
        self.assertEqual(self.change_request.admin_comment, 'Change request denied.')