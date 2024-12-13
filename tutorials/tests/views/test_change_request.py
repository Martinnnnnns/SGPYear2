from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from tutorials.models import Lesson, ProgrammingLanguage, Role, Subject
from tutorials.forms import ChangeBookingForm, CancellationRequestForm
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin, TutorMixin

User = get_user_model()

class BookingViewsTest(RoleSetupTest, StudentMixin, TutorMixin):
    def setUp(self):
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)
        
        self.setup_student()
        self.setup_tutor()

        self.scheduled_lesson = Lesson.objects.create(
            student=self.student_user,
            tutor=self.tutor_user,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() + timedelta(days=1),
            status=Lesson.STATUS_SCHEDULED
        )
        self.completed_lesson = Lesson.objects.create(
            student=self.student_user,
            tutor=self.tutor_user,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() - timedelta(days=1),
            status=Lesson.STATUS_COMPLETED
        )

        self.cancel_url = reverse("request_cancel_bookings", kwargs={"lesson_id": self.scheduled_lesson.id})
        self.dashboard_url = reverse("dashboard")

        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)

    def test_successful_cancellation_request_requires_admin_approval(self):
        """Test that a cancellation request is created and marked for admin approval."""
        form_data = {
            "reason": "Need to cancel due to unforeseen circumstances."
        }
        response = self.client.post(self.cancel_url, form_data, follow=True)
        
        self.scheduled_lesson.refresh_from_db()

        self.assertEqual(self.scheduled_lesson.status, Lesson.STATUS_SCHEDULED)
        self.assertRedirects(response, self.dashboard_url)

    def test_invalid_status_cancellation(self):
        """Test that a completed lesson cannot be canceled."""
        cancel_url = reverse("request_cancel_bookings", kwargs={"lesson_id": self.completed_lesson.id})
        form_data = {
            "reason": "Cannot cancel completed lesson."
        }
        response = self.client.post(cancel_url, form_data)

    def test_permission_denied_for_tutor_cancellation(self):
        """Test that a tutor cannot request cancellation for a lesson."""
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        form_data = {
            "reason": "Tutor trying to cancel a lesson."
        }
        response = self.client.post(self.cancel_url, form_data)

    def test_permission_denied_for_other_student_cancellation(self):
        """Test that a student cannot request cancellation for another student's lesson."""
        other_student_user = User.objects.create_user(
            username="other_student",
            password="Password123",
            email="otherstudent@example.com",
        )
        other_student_user.roles.set([self.student_role])
        self.client.login(username=other_student_user.username, password="Password123")

        form_data = {
            "reason": "Unauthorized cancellation."
        }
        response = self.client.post(self.cancel_url, form_data)
