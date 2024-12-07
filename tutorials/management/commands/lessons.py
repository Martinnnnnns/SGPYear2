import os
from django.core.management.base import BaseCommand
from django.conf import settings
from tutorials.models import Lesson
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create text files with lesson information organized by timeframe'

    def handle(self, *args, **options):
        output_dir = os.path.join(settings.BASE_DIR, 'lessons')
        os.makedirs(output_dir, exist_ok=True)

        lessons = Lesson.objects.all().order_by('lesson_datetime')
        
        timeframes = {
            'past_lessons_7days.txt': self.get_past_lessons_7days,
            'past_lessons_month.txt': self.get_past_lessons_month,
            'past_lessons.txt': self.get_past_lessons,
            'upcoming_lessons.txt': self.get_upcoming_lessons,
            'all_lessons.txt': self.get_all_lessons
        }

        for filename, get_lessons_func in timeframes.items():
            file_path = os.path.join(output_dir, filename)
            filtered_lessons = get_lessons_func(lessons)
            
            with open(file_path, 'w') as f:
                if filtered_lessons:
                    for lesson in filtered_lessons:
                        f.write(self.format_lesson(lesson))
                else:
                    f.write(f'No lessons found for this timeframe\n')

        self.stdout.write(self.style.SUCCESS(f"Lesson files created in '{output_dir}'"))

    def format_lesson(self, lesson):
        return (f"LID: {lesson.id} Student (ID: {lesson.student.id}): {lesson.student.first_name} {lesson.student.last_name} "
                f"Tutor (ID: {lesson.tutor.id}): {lesson.tutor.first_name} {lesson.tutor.last_name} "
                f"Date: {lesson.lesson_datetime.strftime('%Y/%m/%d %H:%M')} "
                f"Programming Language: {lesson.language.name} Subject: {lesson.subject.name}\n")

    def get_past_lessons_7days(self, lessons):
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)
        return [lesson for lesson in lessons if lesson.lesson_datetime < now and lesson.lesson_datetime >= seven_days_ago]

    def get_past_lessons_month(self, lessons):
        now = timezone.now()
        month_ago = now - timedelta(days=30)
        return [lesson for lesson in lessons if lesson.lesson_datetime < now and lesson.lesson_datetime >= month_ago]

    def get_past_lessons(self, lessons):
        now = timezone.now()
        return [lesson for lesson in lessons if lesson.lesson_datetime < now]

    def get_upcoming_lessons(self, lessons):
        now = timezone.now()
        return [lesson for lesson in lessons if lesson.lesson_datetime >= now]

    def get_all_lessons(self, lessons):
        return lessons