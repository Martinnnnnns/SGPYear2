from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Lesson, Subject, ProgrammingLanguage
from django.utils.timezone import now, timedelta

class TutorStudentViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        
        self.tutor = User.objects.create_user(
            username='tutor_test',
            password='Password123',
            email='tutor@test.com',
            first_name='Test',
            last_name='Tutor'
        )
        self.tutor.is_staff = True
        self.tutor.save()
        
        self.student = User.objects.create_user(
            username='student_test',
            password='Password123',
            email='student@test.com',
            first_name='Test',
            last_name='Student'
        )
        
        self.other_student = User.objects.create_user(
            username='other_student',
            password='Password123',
            email='other@test.com'
        )
        
        self.subject = Subject.objects.create(name='Test Subject')
        self.language = ProgrammingLanguage.objects.create(name='Python')
        
        self.future_lesson = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject=self.subject,
            language=self.language,
            lesson_datetime=now() + timedelta(days=1)
        )
        
        self.past_lesson = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject=self.subject,
            language=self.language,
            lesson_datetime=now() - timedelta(days=1)
        )

    def test_tutor_students_list_view_requires_login(self):
        """Test that the tutor students list view requires login"""
        response = self.client.get(reverse('tutor_students_list'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in/'))

    def test_tutor_students_list_view_as_tutor(self):
        """Test that a logged-in tutor can see their students list"""
        self.client.login(username='tutor_test', password='Password123')
        response = self.client.get(reverse('tutor_students_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_students_list.html')
        self.assertContains(response, self.student.email)
        self.assertNotContains(response, self.other_student.email)

    def test_student_profile_detail_requires_login(self):
        """Test that the student profile detail view requires login"""
        response = self.client.get(
            reverse('student_profile_detail', kwargs={'student_id': self.student.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in/'))

    def test_student_profile_detail_as_tutor(self):
        """Test that a tutor can see their student's profile"""
        self.client.login(username='tutor_test', password='Password123')
        response = self.client.get(
            reverse('student_profile_detail', kwargs={'student_id': self.student.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_profile_detail.html')
        self.assertContains(response, self.student.email)
        self.assertContains(response, 'Python')

    def test_tutor_cannot_view_non_student_profile(self):
        """Test that a tutor cannot view profiles of students they don't teach"""
        self.client.login(username='tutor_test', password='Password123')
        response = self.client.get(
            reverse('student_profile_detail', kwargs={'student_id': self.other_student.id})
        )
        self.assertEqual(response.status_code, 403)

    def test_upcoming_and_past_lessons_displayed(self):
        """Test that upcoming and past lessons are correctly displayed"""
        self.client.login(username='tutor_test', password='Password123')
        response = self.client.get(
            reverse('student_profile_detail', kwargs={'student_id': self.student.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upcoming Lessons')
        self.assertContains(response, 'Previous Lessons')
        
        content = str(response.content)
        future_date = self.future_lesson.lesson_datetime.strftime('%B')
        past_date = self.past_lesson.lesson_datetime.strftime('%B')
        
        self.assertIn(future_date, content)
        self.assertIn(past_date, content)