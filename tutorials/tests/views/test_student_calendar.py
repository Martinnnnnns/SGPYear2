from django.urls import reverse
from django.utils import timezone
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin, TutorMixin
from tutorials.models import Lesson, ProgrammingLanguage
from datetime import datetime
import calendar

class StudentLessonCalendarViewTest(RoleSetupTest, StudentMixin, TutorMixin):
    def setUp(self):
        self.setup_student()
        self.setup_tutor()
        self.url = reverse("student_lesson_calendar")
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.client.login(
            username=self.student_user.username, 
            password=RoleSetupTest.PASSWORD
        )

    def create_lesson(self, student, month, year, day):
        return Lesson.objects.create(
            student=student,
            tutor=self.tutor_user,
            language=self.language, 
            lesson_datetime=timezone.make_aware(datetime(year, month, day)),
            status=Lesson.STATUS_SCHEDULED
        )

    def test_view_renders_correctly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_calendar.html")

    def test_view_calendar_data_structure(self):
        response = self.client.get(self.url, {"month": 5, "year": 2024})
        calendar_data = response.context["calendar"]
        self.assertIsInstance(calendar_data, list)
        self.assertTrue(all(isinstance(week, list) for week in calendar_data))

    def test_view_with_lessons(self):
        lesson = self.create_lesson(student=self.student_user, month=5, year=2024, day=15)
        response = self.client.get(self.url, {"month": 5, "year": 2024})
        calendar_data = response.context["calendar"]

        found = False
        for week in calendar_data:
            for day in week:
                if day["day"] == 15:
                    self.assertEqual(len(day["lessons"]), 1)
                    self.assertEqual(day["lessons"][0], lesson)
                    found = True
        self.assertTrue(found)

    def test_view_handles_empty_days(self):
        response = self.client.get(self.url, {"month": 5, "year": 2024})
        calendar_data = response.context["calendar"]

        for week in calendar_data:
            for day in week:
                if day["day"] != 0:
                    self.assertEqual(len(day["lessons"]), 0)

    def test_view_previous_month(self):
        response = self.client.get(self.url, {"month": 1, "year": 2024})
        self.assertEqual(response.context["prev_month"], 12)
        self.assertEqual(response.context["prev_year"], 2023)

    def test_view_next_month(self):
        response = self.client.get(self.url, {"month": 12, "year": 2024})
        self.assertEqual(response.context["next_month"], 1)
        self.assertEqual(response.context["next_year"], 2025)

    def test_view_handles_invalid_month(self):
        with self.assertRaises(calendar.IllegalMonthError):
            self.client.get(self.url, {"month": 13, "year": 2024})