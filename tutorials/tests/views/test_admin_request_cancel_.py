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

from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import AdminMixin, StudentMixin, TutorMixin

User = get_user_model()


class AdminReviewRequestsViewTest(RoleSetupTest, AdminMixin, StudentMixin, TutorMixin):
    def setUp(self):
        self.setup_admin()
        self.setup_tutor()
        self.setup_student()

        self.language = ProgrammingLanguage.objects.create(name='Ruby')
        self.subject = Subject.objects.create(name='Rails', language=self.language)
        self.lesson = Lesson.objects.create(
            student=self.student_user,
            tutor=self.tutor_user,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() + timedelta(days=5),
            status=Lesson.STATUS_SCHEDULED
        )
        self.cancellation_request = CancellationRequest.objects.create(
            user=self.student_user,
            request_type=CancellationRequest.REQUEST_SINGLE,
            reason='Not needed anymore',
            status=CancellationRequest.STATUS_PENDING
        )
        self.cancellation_request.lessons.add(self.lesson)
        self.change_request = ChangeRequest.objects.create(
            user=self.student_user,
            new_datetime=timezone.now() + timedelta(days=6),
            reason='Need to reschedule',
            status=ChangeRequest.STATUS_PENDING
        )
        self.change_request.lessons.add(self.lesson)

    def test_admin_access_required(self):
        response = self.client.get(reverse('admin_review_requests'))
        self.assertRedirects(response, '/log_in/?next=/admin-review/')
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(reverse('admin_review_requests'))
        self.assertEqual(response.status_code, 302)  

    def test_admin_can_view_pending_requests(self):
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(reverse('admin_review_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending Cancellation Requests')
        self.assertContains(response, 'Pending Change Requests')
        self.assertContains(response, self.cancellation_request.reason)
        self.assertContains(response, self.change_request.reason)

    def test_admin_approves_cancellation_request(self):
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        url = reverse('admin_review_requests')
        data = {
            'request_id': self.cancellation_request.id,
            'request_type': 'cancellation',
            'action': 'approve',
            'admin_comment': 'Approved for cancellation.'
        }
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, "Cancellation request approved successfully.")

        self.cancellation_request.refresh_from_db()
        self.lesson.refresh_from_db()

        self.assertEqual(self.cancellation_request.status, CancellationRequest.STATUS_APPROVED)
        self.assertEqual(self.lesson.status, Lesson.STATUS_CANCELED)
        self.assertEqual(self.cancellation_request.admin_comment, 'Approved for cancellation.')

    def test_admin_rejects_cancellation_request(self):
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        url = reverse('admin_review_requests')
        data = {
            'request_id': self.cancellation_request.id,
            'request_type': 'cancellation',
            'action': 'reject',
            'admin_comment': 'Cancellation not approved.'
        }
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, "Cancellation request rejected successfully.")

        self.cancellation_request.refresh_from_db()
        self.lesson.refresh_from_db()

        self.assertEqual(self.cancellation_request.status, CancellationRequest.STATUS_DENIED)
        self.assertEqual(self.lesson.status, Lesson.STATUS_SCHEDULED) 
        self.assertEqual(self.cancellation_request.admin_comment, 'Cancellation not approved.')

    def test_admin_rejects_change_request(self):
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        url = reverse('admin_review_requests')
        data = {
            'request_id': self.change_request.id,
            'request_type': 'change',
            'action': 'reject',
            'admin_comment': 'Change request denied.'
        }
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, "Change request rejected successfully.")

        self.change_request.refresh_from_db()
        self.lesson.refresh_from_db()

        self.assertEqual(self.change_request.status, ChangeRequest.STATUS_DENIED)
        self.assertEqual(self.lesson.lesson_datetime, self.lesson.lesson_datetime) 
        self.assertEqual(self.lesson.status, Lesson.STATUS_SCHEDULED) 
        self.assertEqual(self.change_request.admin_comment, 'Change request denied.')