from django.test import TestCase
from django.utils import timezone
from tutorials.forms import LessonRequestForm
from tutorials.models import ProgrammingLanguage, Subject
from datetime import datetime

class LessonRequestFormTest(TestCase):
    def setUp(self):
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Django", language=self.language)

    def test_valid_data(self):
        data = {
            'date': '2024-12-01', 
            'start_time': '09:00', 
            'end_time': '10:00',   
            'language': self.language.id,
            'subject': self.subject.id,
        }
        
        form = LessonRequestForm(data)
        self.assertTrue(form.is_valid()) 

        #Check cleaned data includes correct datetime objects
        cleaned_data = form.cleaned_data
        self.assertEqual(cleaned_data['start_datetime'], timezone.make_aware(datetime(2024, 12, 1, 9, 0), timezone=timezone.get_default_timezone()))
        self.assertEqual(cleaned_data['end_datetime'], timezone.make_aware(datetime(2024, 12, 1, 10, 0), timezone=timezone.get_default_timezone()))


    def test_valid_data_without_subject(self):
        data = {
            'date': '2024-12-01', 
            'start_time': '09:00', 
            'end_time': '10:00',   
            'language': self.language.id,
            'subject': "",
        }
        
        form = LessonRequestForm(data)
        self.assertTrue(form.is_valid()) 

        #Check cleaned data includes correct datetime objects
        cleaned_data = form.cleaned_data
        self.assertEqual(cleaned_data['start_datetime'], timezone.make_aware(datetime(2024, 12, 1, 9, 0), timezone=timezone.get_default_timezone()))
        self.assertEqual(cleaned_data['end_datetime'], timezone.make_aware(datetime(2024, 12, 1, 10, 0), timezone=timezone.get_default_timezone()))

    def test_missing_required_fields(self):
        data = {
            'date': '2024-12-01',
            'start_time': '09:00',
            'end_time': '10:00',
            'language': '',  
        }
        form = LessonRequestForm(data)
        self.assertFalse(form.is_valid())  
        self.assertIn('language', form.errors)

    def test_time_field_format(self):
        data = {
            'date': '2024-12-01',
            'start_time': '25:00',  
            'end_time': '10:00',
            'language': self.language.id,
            'subject': self.subject.id,
        }
        form = LessonRequestForm(data)
        self.assertFalse(form.is_valid())  
        self.assertIn('start_time', form.errors)
