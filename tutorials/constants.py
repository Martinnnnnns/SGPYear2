#To define user roles for the application

class UserRoles:
    STUDENT = 'student'
    TUTOR = 'tutor'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TUTOR, 'Tutor'),
        (ADMIN, 'Admin'),
    ]


