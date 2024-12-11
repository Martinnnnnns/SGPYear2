from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.constants import UserRoles
from tutorials.models import Lesson, ProgrammingLanguage, Subject, User
from django.utils.timezone import now
from datetime import timedelta

from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import AdminMixin, StudentMixin, TutorMixin


class TutorAvailabilityListViewTests(RoleSetupTest, AdminMixin, TutorMixin, StudentMixin):
    def setUp(self):
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Mathematics", language=self.language)

        self.setup_admin()
        self.setup_tutor()
        self.setup_student()
        self.tutor_2 = User.objects.create_user(
            username="tutor2",
            password="password",      
            email="jhbzh@email.com"
        )
        self.tutor_2.roles.set([self.tutor_role])
        self.tutor_2.current_active_role = self.tutor_role
        self.tutor_2.save()

        self.tutor_3 = User.objects.create_user(
            username="tutor3",
            password="password",
            email="jhvbh@email.com"

        )
        self.tutor_3.roles.set([self.tutor_role])
        self.tutor_3.current_active_role = self.tutor_role
        self.tutor_3.save()

        Lesson.objects.create(
            student=self.admin_user,
            tutor=self.tutor_user,
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

        self.client.login(username=self.admin_user.username, password=RoleSetupTest.PASSWORD)

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
        User.objects.filter(roles__name=UserRoles.TUTOR).delete()
        response = self.client.get(reverse("tutor_availability_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No tutors available")

    def test_tutor_availability_list_view_permission_denied(self):
        """Test that non-admin users cannot access the view."""
        self.client.logout()
        self.client.login(username=self.student_user.username, password=RoleSetupTest.PASSWORD)
        response = self.client.get(reverse("tutor_availability_list"))
        self.assertEqual(response.status_code, 200) 