from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import User, Lesson, Subject, ProgrammingLanguage
from django.db.models import Count

class AdminStatsViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Create roles
        self.admin_user = User.objects.create_user(
            username='admin_user', 
            email='admin@example.com', 
            password='adminpass',
            role='admin'
        )
        self.student_user = User.objects.create_user(
            username='student_user', 
            email='student@example.com', 
            password='studentpass',
            role='student'
        )
        self.tutor_user = User.objects.create_user(
            username='tutor_user', 
            email='tutor@example.com', 
            password='tutorpass',
            role='tutor'
        )

        # Create programming language
        self.language = ProgrammingLanguage.objects.create(name='Python')

        # Create subjects
        self.subject1 = Subject.objects.create(name='Django Basics', language=self.language)
        self.subject2 = Subject.objects.create(name='Flask Advanced', language=self.language)

        # Create lessons
        for i in range(5):
            Lesson.objects.create(
                student=self.student_user,
                tutor=self.tutor_user,
                language=self.language,
                subject=self.subject1,
                lesson_datetime="2024-12-01 10:00"
            )

    def test_admin_can_access_stats(self):
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.get(reverse('admin_stats'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_stats.html')
        self.assertIn('total_lessons', response.context)
        self.assertIn('lessons_per_tutor', response.context)
        self.assertIn('lessons_per_student', response.context)
        self.assertIn('most_popular_languages', response.context)
        self.assertIn('most_popular_subjects', response.context)
        self.assertIn('user_counts_by_role', response.context)
        self.assertIn('language_subject_statistics', response.context)

    def test_non_admin_redirected(self):
        self.client.login(username='student_user', password='studentpass')
        response = self.client.get(reverse('admin_stats'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('access_denied'))

    def test_total_lessons_calculation(self):
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.get(reverse('admin_stats'))
        
        self.assertEqual(response.context['total_lessons'], 5)

    def test_lessons_per_tutor(self):
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.get(reverse('admin_stats'))
        
        lessons_per_tutor = response.context['lessons_per_tutor']
        self.assertEqual(len(lessons_per_tutor), 1) 
        self.assertEqual(lessons_per_tutor[0]['tutor__first_name'], self.tutor_user.first_name)
        self.assertEqual(lessons_per_tutor[0]['lesson_count'], 5)

    def test_lessons_per_student(self):
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.get(reverse('admin_stats'))
        
        lessons_per_student = response.context['lessons_per_student']
        self.assertEqual(len(lessons_per_student), 1)  
        self.assertEqual(lessons_per_student[0]['student__first_name'], self.student_user.first_name)
        self.assertEqual(lessons_per_student[0]['lesson_count'], 5)

    def test_most_popular_languages(self):
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.get(reverse('admin_stats'))
        
        most_popular_languages = response.context['most_popular_languages']
        self.assertEqual(len(most_popular_languages), 1)
        self.assertEqual(most_popular_languages[0]['language__name'], self.language.name)
        self.assertEqual(most_popular_languages[0]['language_count'], 5)

    def test_language_subject_statistics(self):
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.get(reverse('admin_stats'))
        
        language_subject_statistics = response.context['language_subject_statistics']
        self.assertEqual(len(language_subject_statistics), 2)
        self.assertIn({
            'language': self.language.name,
            'subject': self.subject1.name,
            'description': self.subject1.description or 'No description available'
        }, language_subject_statistics)
        self.assertIn({
            'language': self.language.name,
            'subject': self.subject2.name,
            'description': self.subject2.description or 'No description available'
        }, language_subject_statistics)
