from tutorials.models import User, Role
from tutorials.constants import UserRoles

class AdminMixin:
    def setup_admin(self):
        """Create an admin user and set their active role."""
        self.admin_user = User.objects.create_user(
            email="admin@example.com", username="@admin", password="Password123"
        )
        self.admin_user.roles.set([Role.objects.get(name=UserRoles.ADMIN)])
        self.admin_user.current_active_role = self.admin_user.roles.first()  # Set active role
        self.admin_user.save()

class TutorMixin:
    def setup_tutor(self):
        """Create a tutor user and set their active role."""
        self.tutor_user = User.objects.create_user(
            email="tutor@example.com", username="@tutor", password="Password123"
        )
        self.tutor_user.roles.set([Role.objects.get(name=UserRoles.TUTOR)])
        self.tutor_user.current_active_role = self.tutor_user.roles.first()  # Set active role
        self.tutor_user.save()

class StudentMixin:
    def setup_student(self):
        """Create a student user and set their active role."""
        self.student_user = User.objects.create_user(
            email="student@example.com", username="@student", password="Password123"
        )
        self.student_user.roles.set([Role.objects.get(name=UserRoles.STUDENT)])
        self.student_user.current_active_role = self.student_user.roles.first()  # Set active role
        self.student_user.save()

