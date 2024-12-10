from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from tutorials.models import Lesson, Subject, ProgrammingLanguage
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin, TutorMixin

User = get_user_model()

class LessonDetailViewTest(RoleSetupTest, StudentMixin, TutorMixin):
    def setUp(self):
        self.setup_student()
        self.setup_tutor()
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)

        self.language = ProgrammingLanguage.objects.create(name="Python")

        self.subject = Subject.objects.create(name="Django", language=self.language)

        self.lesson = Lesson.objects.create(
            student=self.student_user,
            tutor=self.tutor_user, 
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now()  
        )

    def test_lesson_detail_view(self):
        """Ensure the lesson detail view displays the correct information."""
        response = self.client.get(reverse('lesson_detail', args=[self.lesson.id]))
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'lesson_detail.html')  
        self.assertContains(response, self.lesson.subject.name)  
        self.assertContains(response, self.lesson.language.name)  