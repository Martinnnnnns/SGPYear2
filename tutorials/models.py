from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from libgravatar import Gravatar
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from datetime import datetime, timedelta

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
        return f"{self.language.name} Lesson ({subject_str}) at {self.lesson_datetime} between tutor {self.tutor.full_name()} and student {self.student.full_name()}"

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

class LessonRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_request')
    start_datetime = models.DateTimeField(blank=False)
    end_datetime = models.DateTimeField(blank=False)
    language = models.ForeignKey(ProgrammingLanguage, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    
    def clean(self):
        # Convert naive datetime to aware datetime if needed
        if timezone.is_naive(self.start_datetime):
            self.start_datetime = timezone.make_aware(self.start_datetime)
        if timezone.is_naive(self.end_datetime):
            self.end_datetime = timezone.make_aware(self.end_datetime)

        if not self.is_future_datetime(self.start_datetime):
            raise ValidationError("Lesson must be on a future date and time.")
        if not self.is_future_datetime(self.end_datetime):
            raise ValidationError("Lesson must be on a future date and time.")
        
        if not self.is_end_after_start(self.start_datetime, self.end_datetime):
            raise ValidationError("End time must be after start time.")

        if not self.is_minimum_duration(self.start_datetime, self.end_datetime):
            raise ValidationError("The duration must be at least 30 minutes.")
        
        if self.subject and self.language and not self.is_subject_language_matching(self.subject, self.language):
            raise ValidationError(
                f"{self.subject.name}' isn't a subject of '{self.language}'."
            )
        
        if LessonRequest.objects.filter(user=self.user, start_datetime=self.start_datetime).exists():
            raise ValidationError("A lesson request for this time already exists.")
        
    def is_future_datetime(self, datetime_value):
        """Check if the datetime is in the future."""
        return datetime_value > timezone.now()

    def is_end_after_start(self, start_datetime, end_datetime):
        """Check that the end time is after the start time."""
        return end_datetime > start_datetime

    def is_minimum_duration(self, start_datetime, end_datetime):
        """Check that the duration is at least 30 minutes."""
        return end_datetime - start_datetime >= timedelta(minutes=30)

    def is_subject_language_matching(self, subject, language):
        """Check that the subject belongs to the correct language."""
        return subject.language == language
        
    def __str__(self):
        subject_name = self.subject.name if self.subject else "No subject"
        return f"Lesson Request by {self.user.username} ({subject_name} - {self.language.name}) from {self.start_datetime.strftime('%Y-%m-%d %H:%M')} to {self.end_datetime.strftime('%Y-%m-%d %H:%M')}"

class TutorAvailability(models.Model):
    """Model to store tutor availability slots."""
    RECURRENCE_CHOICES = [
        ('none', 'One-time'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
    ]
    
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='none')
    end_recurrence_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        verbose_name_plural = "Tutor availabilities"