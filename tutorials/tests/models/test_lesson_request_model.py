from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.timezone import now, timedelta, make_naive, make_aware
from tutorials.models import LessonRequest, User, ProgrammingLanguage, Subject
from datetime import timezone, datetime
from django.utils import timezone as django_timezone  
from pytz import UTC

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
            
    def test_naive_start_datetime_conversion(self):
        start_time_naive = make_naive(now() + timedelta(hours=1))
        end_time = start_time_naive + timedelta(hours=1)
        lesson = LessonRequest(
            user=self.user,
            start_datetime=start_time_naive,
            end_datetime=end_time,
            language=self.language,
            subject=self.subject,
        )
        lesson.start_datetime = make_aware(lesson.start_datetime, timezone.utc)
        lesson.end_datetime = make_aware(lesson.end_datetime, timezone.utc)
        lesson.clean()
        self.assertTrue(lesson.start_datetime.tzinfo is not None and lesson.start_datetime.tzinfo.utcoffset(lesson.start_datetime) == timedelta(0))

    def test_naive_end_datetime_conversion(self):
        start_time = now() + timedelta(hours=1)
        end_time_naive = make_naive(start_time + timedelta(hours=1))
        lesson = LessonRequest(
            user=self.user,
            start_datetime=start_time,
            end_datetime=end_time_naive,
            language=self.language,
            subject=self.subject,
        )
        lesson.end_datetime = make_aware(lesson.end_datetime, timezone.utc)

        lesson.clean()
        self.assertTrue(lesson.end_datetime.tzinfo is not None and lesson.end_datetime.tzinfo.utcoffset(lesson.end_datetime) == timedelta(0))


    def test_start_datetime_not_in_future(self):
        past_start_time = now() - timedelta(days=1)
        end_time = past_start_time + timedelta(hours=1)
        lesson = LessonRequest(
            user=self.user,
            start_datetime=past_start_time,
            end_datetime=end_time,
            language=self.language,
            subject=self.subject,
        )
        with self.assertRaises(ValidationError) as context:
            lesson.clean()
        self.assertIn("Lesson must be on a future date and time.", str(context.exception))

    def test_end_datetime_not_in_future(self):
        start_time = now() + timedelta(hours=1)
        past_end_time = now() - timedelta(days=1)
        lesson = LessonRequest(
            user=self.user,
            start_datetime=start_time,
            end_datetime=past_end_time,
            language=self.language,
            subject=self.subject,
        )
        with self.assertRaises(ValidationError) as context:
            lesson.clean()
        self.assertIn("Lesson must be on a future date and time.", str(context.exception))

    def test_both_datetimes_conversion(self):
        naive_start_time = datetime.now() + timedelta(days=1)
        naive_end_time = naive_start_time + timedelta(hours=2)
        
        lesson = LessonRequest(
            user=self.user,
            start_datetime=naive_start_time,
            end_datetime=naive_end_time,
            language=self.language,
            subject=self.subject
        )

        self.assertTrue(django_timezone.is_naive(lesson.start_datetime))
        self.assertTrue(django_timezone.is_naive(lesson.end_datetime))

        original_utc = getattr(django_timezone, 'utc', None)
        django_timezone.utc = UTC
        try:
            lesson.clean()
        finally:
            if original_utc is not None:
                django_timezone.utc = original_utc
            else:
                delattr(django_timezone, 'utc')

        self.assertTrue(django_timezone.is_aware(lesson.start_datetime))
        self.assertTrue(django_timezone.is_aware(lesson.end_datetime))

