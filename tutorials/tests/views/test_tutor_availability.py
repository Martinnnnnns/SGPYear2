from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Lesson, ProgrammingLanguage, Subject
from django.utils.timezone import now
from datetime import timedelta

User = get_user_model()


class TutorAvailabilityListViewTests(TestCase):
    def setUp(self):
        # Create programming language and subject
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)

        # Create admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            password="password",
            role="admin",
            email="jhbh@email.com"
        )
        
        # Create tutors
        self.tutor_1 = User.objects.create_user(
            username="tutor1",
            password="password",
            role="tutor",            
            email="jhsbh@email.com"

            
        )
        self.tutor_2 = User.objects.create_user(
            username="tutor2",
            password="password",
            role="tutor",           
            email="jhbzh@email.com"


            
        )
        self.tutor_3 = User.objects.create_user(
            username="tutor3",
            password="password",
            role="tutor",           
            email="jhvbh@email.com"

        )

        # Create lessons
        Lesson.objects.create(
            student=self.admin_user,
            tutor=self.tutor_1,
            language=self.language,
            subject=self.subject,
            lesson_datetime=now() + timedelta(days=1),
            status=Lesson.STATUS_SCHEDULED,
        )
        Lesson.objects.create(
            student=self.admin_user,
            tutor=self.tutor_2,
            language=self.language,
            subject=self.subject,
            lesson_datetime=now() + timedelta(days=1),
            status=Lesson.STATUS_SCHEDULED,
        )
        Lesson.objects.create(
            student=self.admin_user,
            tutor=self.tutor_2,
            language=self.language,
            subject=self.subject,
            lesson_datetime=now() + timedelta(days=2),
            status=Lesson.STATUS_SCHEDULED,
        )

        # Log in as admin
        self.client.login(username="admin", password="password")

    def test_tutor_availability_list_view_status_code(self):
        """Test that the view returns a 200 status code."""
        response = self.client.get(reverse("tutor_availability_list"))
        self.assertEqual(response.status_code, 200)

    def test_tutor_availability_list_view_template_used(self):
        """Test that the correct template is used."""
        response = self.client.get(reverse("tutor_availability_list"))
        self.assertTemplateUsed(response, "tutor_availability_list.html")
        self.assertTemplateUsed(response, "base_content.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "partials/navbar.html")
        self.assertTemplateUsed(response, "partials/menu.html")
        self.assertTemplateUsed(response, "partials/messages.html")
        

    def test_tutor_availability_list_view_tutor_count(self):
        """Test that all tutors are included in the response context."""
        response = self.client.get(reverse("tutor_availability_list"))
        self.assertEqual(len(response.context["tutors"]), 3)

    

    def test_tutor_availability_list_view_no_tutors(self):
        """Test that the view handles cases with no tutors gracefully."""
        User.objects.filter(role="tutor").delete()
        response = self.client.get(reverse("tutor_availability_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No tutors available")

    def test_tutor_availability_list_view_permission_denied(self):
        """Test that non-admin users cannot access the view."""
        self.client.logout()
        student_user = User.objects.create_user(
            username="student",
            password="password",
            role="student"
        )
        self.client.login(username="student", password="password")
        response = self.client.get(reverse("tutor_availability_list"))
        self.assertEqual(response.status_code, 200)  # Forbidden