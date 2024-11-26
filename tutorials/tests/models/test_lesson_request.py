from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.timezone import now, timedelta
from tutorials.models import LessonRequest, User, ProgrammingLanguage, Subject

class LessonRequestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Django", language=self.language)
        self.start_datetime = now() + timedelta(days=1)  
        self.end_datetime = self.start_datetime + timedelta(hours=1) 
        self.lesson_request = LessonRequest.objects.create(
            user=self.user,
            start_datetime=self.start_datetime,
            end_datetime=self.end_datetime,
            language=self.language,
            subject=self.subject,
        )

    def test_lesson_request_str_method(self):
        expected_str = (
            f"Lesson Request by {self.user.username} "
            f"({self.subject.name} - {self.language.name}) from "
            f"{self.start_datetime.strftime('%Y-%m-%d %H:%M')} to "
            f"{self.end_datetime.strftime('%Y-%m-%d %H:%M')}"
        )
        self.assertEqual(str(self.lesson_request), expected_str)


    def test_valid_lesson_request(self):
        start_time = now() + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=45)
        lesson = LessonRequest(
            user=self.user,
            start_datetime=start_time,
            end_datetime=end_time,
            language=self.language,
            subject=self.subject
        )
        try:
            lesson.clean() 
        except ValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")

    def test_start_time_not_in_future(self):
        start_time = now() - timedelta(hours=1)
        end_time = now() + timedelta(hours=1)
        lesson = LessonRequest(
            user=self.user,
            start_datetime=start_time,
            end_datetime=end_time,
            language=self.language,
            subject=self.subject
        )
        with self.assertRaises(ValidationError):
            lesson.clean()

    def test_end_time_before_start_time(self):
        start_time = now() + timedelta(hours=1)
        end_time = start_time - timedelta(minutes=30)
        lesson = LessonRequest(
            user=self.user,
            start_datetime=start_time,
            end_datetime=end_time,
            language=self.language,
            subject=self.subject
        )
        with self.assertRaises(ValidationError):
            lesson.clean()

    def test_duration_too_short(self):
        start_time = now() + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=20)
        lesson = LessonRequest(
            user=self.user,
            start_datetime=start_time,
            end_datetime=end_time,
            language=self.language,
            subject=self.subject
        )
        with self.assertRaises(ValidationError):
            lesson.clean()

    def test_subject_language_mismatch(self):
        other_language = ProgrammingLanguage.objects.create(name="JavaScript")
        mismatched_subject = Subject.objects.create(name="React", language=other_language)
        start_time = now() + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=45)
        lesson = LessonRequest(
            user=self.user,
            start_datetime=start_time,
            end_datetime=end_time,
            language=self.language,
            subject=mismatched_subject
        )
        with self.assertRaises(ValidationError):
            lesson.clean()

    def test_duplicate_lesson_request(self):
        start_time = now() + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=45)
        LessonRequest.objects.create(
            user=self.user,
            start_datetime=start_time,
            end_datetime=end_time,
            language=self.language,
            subject=self.subject
        )
        duplicate_lesson = LessonRequest(
            user=self.user,
            start_datetime=start_time,
            end_datetime=end_time,
            language=self.language,
            subject=self.subject
        )
        with self.assertRaises(ValidationError):
            duplicate_lesson.clean()

    def test_valid_lesson_request_without_subject(self):
        start_time = now() + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=45)
        lesson = LessonRequest(
            user=self.user,
            start_datetime=start_time,
            end_datetime=end_time,
            language=self.language,
            subject=None
        )
        try:
            lesson.clean()
        except ValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")