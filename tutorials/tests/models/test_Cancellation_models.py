# tutorials/tests/test_models.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import CancellationRequest, ChangeRequest, Lesson, ProgrammingLanguage, Subject, TutorAvailability
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()


class CancellationRequestModelTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student2', email='student2@example.com', password='testpass')
        self.tutor = User.objects.create_user(username='tutor2', email='tutor2@example.com', password='testpass')
        self.language = ProgrammingLanguage.objects.create(name='JavaScript')
        self.subject = Subject.objects.create(name='React',language=self.language)
        self.lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() + timedelta(days=2),
            status=Lesson.STATUS_SCHEDULED
        )
        self.cancellation_request = CancellationRequest.objects.create(
            user=self.student,
            request_type=CancellationRequest.REQUEST_SINGLE,
            reason='Personal reasons',
            status=CancellationRequest.STATUS_PENDING
        )
        self.cancellation_request.lessons.add(self.lesson)

    def test_cancellation_request_creation(self):
        self.assertEqual(self.cancellation_request.user, self.student)
        self.assertEqual(self.cancellation_request.status, CancellationRequest.STATUS_PENDING)
        self.assertIn(self.lesson, self.cancellation_request.lessons.all())

    def test_process_approval(self):
        self.cancellation_request.process_approval()
        self.cancellation_request.refresh_from_db()
        self.lesson.refresh_from_db()
        self.assertEqual(self.cancellation_request.status, CancellationRequest.STATUS_APPROVED)
        self.assertEqual(self.lesson.status, Lesson.STATUS_CANCELED)

    def test_process_rejection(self):
        self.cancellation_request.process_rejection()
        self.cancellation_request.refresh_from_db()
        self.assertEqual(self.cancellation_request.status, CancellationRequest.STATUS_DENIED)

    def test_invalid_status_assignment(self):
        with self.assertRaises(ValidationError):
            self.cancellation_request.status = 'invalid_status'
            self.cancellation_request.full_clean()

class ChangeRequestModelTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student3', email='student3@example.com', password='testpass')
        self.tutor = User.objects.create_user(username='tutor3', email='tutor3@example.com', password='testpass')
        self.language = ProgrammingLanguage.objects.create(name='Java')
        self.subject = Subject.objects.create(name='Spring',language=self.language)
        self.lesson = Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            language=self.language,
            subject=self.subject,
            lesson_datetime=timezone.now() + timedelta(days=3),
            status=Lesson.STATUS_SCHEDULED
        )
        self.change_request = ChangeRequest.objects.create(
            user=self.student,
            new_datetime=timezone.now() + timedelta(days=4),
            reason='Schedule conflict',
            status=ChangeRequest.STATUS_PENDING
        )
        self.change_request.lessons.add(self.lesson)

    def test_change_request_creation(self):
        self.assertEqual(self.change_request.user, self.student)
        self.assertEqual(self.change_request.status, ChangeRequest.STATUS_PENDING)
        self.assertIn(self.lesson, self.change_request.lessons.all())

    def test_process_approval(self):
        # Mock tutor availability
        new_datetime = self.change_request.new_datetime  # This is a datetime object
        TutorAvailability.objects.create(
            tutor=self.tutor,
            date=new_datetime.date(),
            start_time=(datetime.combine(new_datetime.date(), new_datetime.time()) - timedelta(hours=1)).time(),
            end_time=(datetime.combine(new_datetime.date(), new_datetime.time()) + timedelta(hours=1)).time()
)
        self.assertTrue(self.change_request.is_within_tutor_availability())
        self.change_request.process_approval()
        self.change_request.refresh_from_db()
        self.lesson.refresh_from_db()
        self.assertEqual(self.change_request.status, ChangeRequest.STATUS_APPROVED)
        self.assertEqual(self.lesson.lesson_datetime, self.change_request.new_datetime)
        self.assertEqual(self.lesson.status, Lesson.STATUS_RESCHEDULED)

    def test_process_rejection(self):
        self.change_request.process_rejection()
        self.change_request.refresh_from_db()
        self.assertEqual(self.change_request.status, ChangeRequest.STATUS_DENIED)

    def test_is_within_tutor_availability_false(self):
        self.assertFalse(self.change_request.is_within_tutor_availability())

    def test_invalid_status_assignment(self):
        with self.assertRaises(ValidationError):
            self.change_request.status = 'invalid_status'
            self.change_request.full_clean()