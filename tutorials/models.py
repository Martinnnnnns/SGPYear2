from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.contrib.auth.models import User


class User(AbstractUser):
    """Model used for user authentication, and team member-related information."""
    USER_TYPES=[
        ('tutor','Tutor'),
        ('student','Student'),
    ]
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPES, 
        default='student',
        verbose_name='User Type')

    class Meta:
        """Model options."""
        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

class Lesson(models.Model):
    """Model for storing lesson information."""
    tutor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="lessons_as_tutor"
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="lessons_as_student"
    )
    subject = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    duration = models.DurationField()  # e.g., timedelta(hours=1)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
<<<<<<< Updated upstream
        return f"{self.subject} - {self.tutor.username} tutoring {self.student.username}"
=======
        subject_str = self.subject.name if self.subject else "General"
        return f"Lesson in {self.language.name} ({subject_str}) at {self.lesson_datetime}"

    def clean(self):
        """Ensure that if a subject is provided, its language matches the lesson's language"""
        if self.subject and self.subject.language and self.subject.language != self.language:
            raise ValidationError(f"The subject's language ({self.subject.language.name}) does not match the lesson's language ({self.language.name}).")

    def save(self, *args, **kwargs):
        """Run validation before saving"""
        self.clean()
        super().save(*args, **kwargs)

    def get_language(self):
        """Returns the language directly if there's no subject; otherwise, it derives from the subject"""
        return self.subject.language if self.subject else self.language
    
    class Meta:
        ordering = ["tutor", "student", "language", 'subject']
        
class Invoice(models.Model):
    """
    Represents an invoice for a student.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=[
            ('paid', 'Paid'),
            ('unpaid', 'Unpaid'),
        ]
    )

    def __str__(self):
        return f"Invoice {self.id} for {self.student.username} - {self.status}"
>>>>>>> Stashed changes
