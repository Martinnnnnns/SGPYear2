from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""
    
    # User role choices
    STUDENT = 'student'
    TUTOR = 'tutor'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TUTOR, 'Tutor'),
        (ADMIN, 'Admin'),
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
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=STUDENT,
    )

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
    
class ProgrammingLanguage(models.Model):
    """Model for programming languages that we offer lessons in."""
    name = models.CharField(max_length=100, unique=True, blank=False)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Subject(models.Model):
    """Model for topics that a lesson in a given programming langauge can be about."""
    name = models.CharField(max_length=100)
    language = models.ForeignKey(ProgrammingLanguage, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)  

    def __str__(self):
        return f"{self.language.name} - {self.name} - {self.description or 'No description'}"
    
    class Meta:
        ordering = ["language", 'name']

class Lesson(models.Model):
    """Model for lessons that admins can book. Subjects are optional but must map correctly to a language."""
    student = models.ForeignKey(User, related_name='lessons_as_student', on_delete=models.CASCADE)
    tutor = models.ForeignKey(User, related_name='lessons_as_tutor', on_delete=models.CASCADE)
    language = models.ForeignKey(ProgrammingLanguage, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    lesson_datetime = models.DateTimeField(null=False)

    def __str__(self):
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

