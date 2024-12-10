from django.core.management.base import BaseCommand, CommandError
from tutorials.models import User, ProgrammingLanguage, Subject, Lesson, Role, LessonRequest

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        """Unseed the database."""

        Role.objects.all().delete()
        User.objects.filter().delete()
        ProgrammingLanguage.objects.filter().delete() 
        Subject.objects.filter().delete()
        LessonRequest.objects.filter().delete() 
        Lesson.objects.filter().delete()