from django.core.management.base import BaseCommand, CommandError
from tutorials.models import User, ProgrammingLanguage, Subject, Lesson

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        """Unseed the database."""

        User.objects.filter(is_staff=False).delete()
        ProgrammingLanguage.objects.filter().delete() 
        Subject.objects.filter().delete() 
        Lesson.objects.filter().delete()