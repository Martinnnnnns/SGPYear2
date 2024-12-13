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
            start_datetime=now() + timedelta(hours=1), 
            end_datetime=now() + timedelta(hours=2),
        )

    def test_trigger_matching_url(self):
        """Test that the trigger matching URL resolves correctly."""
        self.assertEqual(self.url, '/trigger_matching/')  

    def test_trigger_matching_requires_login(self):
        """Test that the view requires login."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302) 

    def test_trigger_matching_as_admin(self):
        """Test that the view works as expected for admin users."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(LessonRequest.objects.count(), 1)
        lesson = LessonRequest.objects.first()
        self.assertEqual(lesson.user, self.student_user)

    def test_trigger_matching_no_tutors(self):
        """Test that no lesson is created if no tutors are available."""
        self.tutor_user.delete() 
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_trigger_matching_template(self):
        """Test that the correct template is rendered."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, 'trigger_matching.html')
    def test_trigger_matching_creates_lesson(self):
        """Test that a valid lesson request creates a lesson."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.post(self.url, data={
            f'lesson_request_{self.lesson_request.id}': self.tutor_user.id
        })
        self.assertEqual(response.status_code, 200)

        lesson = Lesson.objects.first()
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson.student, self.student_user)
        self.assertEqual(lesson.tutor, self.tutor_user)
    def test_permission_denied_for_non_admin_user(self):
        """Test that non-admin users cannot access the view."""
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)

        # Simulate POST data
        data = {f'lesson_request_{self.lesson_request.id}': self.tutor_user.id}
        response = self.client.post(self.url, data=data)

        # Verify the response and that no lesson is created
        self.assertEqual(response.status_code, 302)  # Forbidden
        self.assertEqual(Lesson.objects.count(), 0)
    
    def test_invalid_lesson_request(self):
        """Test handling of invalid lesson requests."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)

        # Simulate POST data with an invalid lesson request ID
        data = {f'lesson_request_invalid': self.tutor_user.id}
        response = self.client.post(self.url, data=data)

        # Verify that no lesson is created
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_successful_tutor_matching(self):
        """Test that a tutor is successfully matched to a lesson request."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        
        # Simulate POST data
        data = {f'lesson_request_{self.lesson_request.id}': self.tutor_user.id}
        response = self.client.post(self.url, data=data)

        # Verify the response and database updates
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lesson.objects.count(), 1)

        lesson = Lesson.objects.first()
        self.assertEqual(lesson.student, self.student_user)
        self.assertEqual(lesson.tutor, self.tutor_user)
        self.assertEqual(lesson.lesson_datetime, self.lesson_request.start_datetime)

        # Check the lesson request status
        self.lesson_request.refresh_from_db()
        self.assertEqual(self.lesson_request.status, 'allocated')
                    