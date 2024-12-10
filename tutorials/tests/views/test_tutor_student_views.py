from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Lesson, Subject, ProgrammingLanguage, User
from django.utils.timezone import now, timedelta
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin, TutorMixin

class TutorStudentViewsTest(RoleSetupTest, StudentMixin, TutorMixin):
    def setUp(self):
        self.client = Client()
        self.setup_student()
        self.setup_tutor()
  
        self.other_student = User.objects.create_user(
            username='@other_student',
            password='Password123',
            email='other@test.com',
            first_name='Other',
            last_name='Student',
        )
        self.other_student.roles.set([self.student_role])
        self.other_student.current_active_role = self.student_role
        self.other_student.save()
        
        self.language = ProgrammingLanguage.objects.create(name='Python')
        
        self.subject = Subject.objects.create(
            name='Test Subject',
            language=self.language
        )
        
        self.future_lesson = Lesson.objects.create(
            tutor=self.tutor_user,
            student=self.student_user,
            subject=self.subject,
            language=self.language,
            lesson_datetime=now() + timedelta(days=1)
        )
        
        self.past_lesson = Lesson.objects.create(
            tutor=self.tutor_user,
            student=self.student_user,
            subject=self.subject,
            language=self.language,
            lesson_datetime=now() - timedelta(days=1)
        )

        self.tutor_students_list_url = reverse('tutor_students_list')
        self.student_profile_url = lambda student_id: reverse('student_profile_detail', kwargs={'student_id': student_id})

    def test_tutor_students_list_view_requires_login(self):
        response = self.client.get(reverse('tutor_students_list'))
        self.assertEqual(response.status_code, 302)
        expected_url = f"/log_in/?next={reverse('tutor_students_list')}"
        self.assertEqual(response.url, expected_url)

    def test_tutor_students_list_view_as_tutor(self):
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(reverse('tutor_students_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_students_list.html')

    def test_student_profile_detail_requires_login(self):
        url = reverse('student_profile_detail', kwargs={'student_id': self.student.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        expected_url = f"/log_in/?next={url}"
        self.assertEqual(response.url, expected_url)

    def test_student_profile_detail_as_tutor(self):
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(
            reverse('student_profile_detail', kwargs={'student_id': self.student_user.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_profile_detail.html')
        self.assertContains(response, self.student_user.email)
        self.assertContains(response, 'Python')

    def test_tutor_cannot_view_non_student_profile(self):
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(
            reverse('student_profile_detail', kwargs={'student_id': self.other_student.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_tutor_students_list_view_as_student(self):
        """Test that a student user is redirected to access denied page."""
        self.client.login(username='@student_test', password='Password123')
        response = self.client.get(self.tutor_students_list_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/access_denied')

    def test_student_profile_detail_as_student(self):
        """Test that a student user is redirected to access denied page."""
        self.client.login(username='@student_test', password='Password123')
        response = self.client.get(self.student_profile_url(self.other_student.id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/access_denied')

    def test_student_profile_detail_invalid_student(self):
        """Test accessing a non-existent student profile."""
        self.client.login(username='@tutor_test', password='Password123')
        response = self.client.get(self.student_profile_url(99999))
        self.assertEqual(response.status_code, 404)

    def test_current_students_list_view_requires_tutor_role(self):
        """Test that current students list requires tutor role."""
        self.client.login(username='@student_test', password='Password123')
        response = self.client.get(reverse('current_students'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/access_denied')

    def test_previous_students_list_view_requires_tutor_role(self):
        """Test that previous students list requires tutor role."""
        self.client.login(username='@student_test', password='Password123')
        response = self.client.get(reverse('previous_students'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/access_denied')

    def test_upcoming_and_past_lessons_displayed(self):
        self.client.login(username=self.tutor_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(
            reverse('student_profile_detail', kwargs={'student_id': self.student_user.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upcoming Lessons')
        self.assertContains(response, 'Previous Lessons')
        
        content = str(response.content)
        future_date = self.future_lesson.lesson_datetime.strftime('%B')
        past_date = self.past_lesson.lesson_datetime.strftime('%B')
        
        self.assertIn(future_date, content)
        self.assertIn(past_date, content)
