from django.urls import reverse
from tutorials.models import ProgrammingLanguage, Subject
from django.utils import timezone
from tutorials.forms import LessonRequestForm
from tutorials.models import LessonRequest
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin
import warnings

class LessonRequestViewTest(RoleSetupTest, StudentMixin):
    def setUp(self):
        self.setup_student()
        self.url = reverse("request_lesson")

        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)

        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*naive datetime.*")

        now = timezone.now()
        next_full_hour = now.replace(minute=0, second=0, microsecond=0) + timezone.timedelta(hours=1)
        start = next_full_hour
        end = start + timezone.timedelta(minutes=30)

        self.data =  {
            'date': start.strftime("%Y-%m-%d"),
            'start_time': start.time().strftime('%H:%M'), 
            'end_time': end.time().strftime('%H:%M'),    
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
        self.assertEqual(after_count, before_count) #Expect no increase as this LessonRequest should not have been made
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "make_lesson_request.html") 
        self.assertIn("form", response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, LessonRequestForm))
        self.assertTrue(form.is_bound) #This time with a bounded form (prev inputted data)
