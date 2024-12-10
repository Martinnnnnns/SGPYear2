from django.urls import reverse
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin

class LessonRequestViewTest(RoleSetupTest, StudentMixin):
    def setUp(self):
        self.setup_student()
        self.url = reverse("request_made")
        self.client.login(username=self.student_user.username, 
                          password=RoleSetupTest.PASSWORD)

    def test_request_made_url(self):
        self.assertEqual(self.url, "/request_made/")

    def test_get_request_lesson(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "make_another_request.html")

    def test_load_make_lesson_request_page_again(self):
        make_another_url = reverse('request_lesson')
        response = self.client.get(make_another_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'make_lesson_request.html')

    def test_go_to_homepage(self):
        return_home_url = reverse('dashboard')
        response = self.client.get(return_home_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_dashboard.html')
