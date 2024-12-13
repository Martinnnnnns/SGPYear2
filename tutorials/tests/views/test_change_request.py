from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now, timedelta
from tutorials.models import User, Lesson, ChangeRequest, ProgrammingLanguage, Subject
from tutorials.forms import ChangeBookingForm

class RequestChangeBookingsViewTestCase(TestCase):
    def setUp(self):
        # Create users
        self.student = User.objects.create_user(
            username="student",
            password="password123",
            email="student@example.com"
        )
        self.student.roles.create(name="student")
        self.student.current_active_role = self.student.roles.first()
        self.student.save()

        # Create a tutor user
        self.tutor = User.objects.create_user(
            username="tutor",
            password="password123",
            email="tutor@example.com"
        )
        self.tutor.roles.create(name="tutor")
        self.tutor.current_active_role = self.tutor.roles.first()
        self.tutor.save()

        # Create programming language and subject
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Intro to Python", language=self.language)

        # Create a lesson
        self.lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            lesson_datetime=now() + timedelta(days=2),
            language=self.language,
            subject=self.subject,
            status=Lesson.STATUS_SCHEDULED,
        )

        # Define the URL
        self.url = reverse("request_change_bookings", kwargs={"lesson_id": self.lesson.id})

    def test_view_access_student(self):
        """Test that the view is accessible for the student."""
        self.client.login(username="student", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "request_change_bookings.html")

    def test_view_access_tutor(self):
        """Test that the view is accessible for the tutor."""
        self.client.login(username="tutor", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "request_change_bookings.html")

    def test_view_access_unauthorized_user(self):
        """Test that an unauthorized user cannot access the view."""
        other_user = User.objects.create_user(username="other_user", password="password123", email="other@example.com")
        self.client.login(username="other_user", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_form_initial_data(self):
        """Test that the form is prepopulated with the lesson's current date and time."""
        self.client.login(username="student", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.context["form"].initial["new_datetime"], self.lesson.lesson_datetime)

    def test_successful_change_request(self):
        """Test submitting a valid change request."""
        self.client.login(username="student", password="password123")
        new_datetime = now() + timedelta(days=3)
        data = {
            "new_datetime": new_datetime,
            "reason": "Change needed for personal reasons",
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard"))

        change_request = ChangeRequest.objects.first()
        self.assertIsNotNone(change_request)
        self.assertEqual(change_request.user, self.student)
        self.assertEqual(change_request.new_datetime, new_datetime)
        self.assertEqual(change_request.reason, "Change needed for personal reasons")
        self.assertIn(self.lesson, change_request.lessons.all())

    def test_invalid_form_submission(self):
        """Test submitting an invalid form."""
        self.client.login(username=self.student.username, password="password123")
        data = {"new_datetime": ""}  
        response = self.client.post(self.url, data=data)
        response.render()  
        self.assertFormError(response, "form", "new_datetime", "This field is required.")

    def test_context_data(self):
        """Test that the lesson is included in the context."""
        self.client.login(username="student", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.context["lesson"], self.lesson)