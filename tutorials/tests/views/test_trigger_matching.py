from django.urls import reverse
from django.utils.timezone import now
from datetime import timedelta
from tutorials.models import User, ProgrammingLanguage, Subject, LessonRequest, Lesson
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin, TutorMixin, AdminMixin
import uuid

class TriggerMatchingTestCase(RoleSetupTest, AdminMixin, StudentMixin, TutorMixin):
    def setUp(self):
        self.url = reverse('trigger_matching')
        self.setup_admin()
        self.setup_tutor()
        self.setup_student()

        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Intro to Python", language=self.language)

        self.lesson_request = LessonRequest.objects.create(
            user=self.student_user,
            language=self.language,
            subject=self.subject,
            start_datetime=now() + timedelta(hours=1),  # Ensure future datetime
            end_datetime=now() + timedelta(hours=2),
        )

    def test_trigger_matching_url(self):
        """Test that the trigger matching URL resolves correctly."""
        self.assertEqual(self.url, '/trigger_matching/')  # Match the URL pattern

    def test_trigger_matching_requires_login(self):
        """Test that the view requires login."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_trigger_matching_as_admin(self):
        """Test that the view works as expected for admin users."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

        # Verify the lesson was created
        self.assertEqual(Lesson.objects.count(), 1)
        lesson = Lesson.objects.first()
        self.assertEqual(lesson.student, self.student_user)
        self.assertEqual(lesson.tutor, self.tutor_user)

    def test_trigger_matching_no_tutors(self):
        """Test that no lesson is created if no tutors are available."""
        self.tutor_user.delete()  # Remove the tutor

        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

        # Verify no lessons were created
        self.assertEqual(Lesson.objects.count(), 0)

    def test_trigger_matching_template(self):
        """Test that the correct template is rendered."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, 'trigger_matching.html')