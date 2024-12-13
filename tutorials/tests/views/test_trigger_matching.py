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
    
    
    
    def test_trigger_matching_view_get(self):
        
        """Test that the GET request correctly displays pending lesson requests and available tutors."""
        self.tutor_user.availability_slots.create(
            date=self.lesson_request.start_datetime.date(),
            start_time=self.lesson_request.start_datetime.time(),
            end_time=self.lesson_request.end_datetime.time(),
        )

        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_trigger_matching_invalid_tutor(self):
        """Test that an invalid tutor ID does not create a lesson."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        post_data = {
            f'lesson_request_{self.lesson_request.id}': 9999,  # Invalid tutor ID
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lesson.objects.count(), 0)  # No lessons created

    def test_trigger_matching_unmatched_requests(self):
        """Test that unmatched requests are handled correctly."""
        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)
        post_data = {
            f'lesson_request_{self.lesson_request.id}': 9999,  # Invalid tutor ID
        }
        response = self.client.post(self.url, post_data)

        self.assertEqual(response.status_code, 200)
        # Verify unmatched request
        self.assertEqual(Lesson.objects.count(), 0)  # No lessons created
        unmatched_requests = response.context['unmatched_requests']
        self.assertIn(self.lesson_request, unmatched_requests)
