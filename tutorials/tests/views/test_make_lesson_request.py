from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import ProgrammingLanguage, Subject, User
from django.utils import timezone

from tutorials.forms import LessonRequestForm
from tutorials.models import LessonRequest

User = get_user_model()

class LessonRequestViewTest(TestCase):
    def setUp(self):
        self.url = reverse("request_lesson")
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='testuser@example.com',
            first_name='John',
            last_name='Doe'
        )

        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)

        self.client.login(username='testuser', password='password123')

        now = timezone.now()
        next_full_hour = now.replace(minute=0, second=0, microsecond=0) + timezone.timedelta(hours=1)
        start = next_full_hour
        end = start + timezone.timedelta(minutes=30)

        self.data =  {
            'date': start.strftime("%Y-%m-%d"),
            'start_time': start.strftime('%H:%M'), 
            'end_time': end.strftime('%H:%M'),    
            'language': self.language.id,
            'subject': self.subject.id
        }

    def test_request_lesson_url(self):
        self.assertEqual(self.url, "/request_lesson/")

    def test_get_request_lesson(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "make_lesson_request.html")
        self.assertIn("form", response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, LessonRequestForm))
        self.assertFalse(form.is_bound)

    def test_post_with_valid_data(self):
        before_count = LessonRequest.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        after_count = LessonRequest.objects.count()
        self.assertEqual(after_count, before_count + 1)

        expected_redirect_url = reverse('request_made')
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

    def test_post_with_invalid_data(self):
        self.data['language'] = ""
        before_count = LessonRequest.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        after_count = LessonRequest.objects.count()
        self.assertEqual(after_count, before_count) #expect no increase as this LessonRequest should not habe been made
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "make_lesson_request.html") 
        self.assertIn("form", response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, LessonRequestForm))
        self.assertTrue(form.is_bound) #but this time with a bounded form (prev inputted data)
