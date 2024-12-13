from django.test import TestCase
from tutorials.models import ProgrammingLanguage
from django.db import IntegrityError
from django.core.exceptions import ValidationError

class ProgrammingLanguageTestCase(TestCase):
    def setUp(self):
        self.language = ProgrammingLanguage.objects.create(name="Python")

    def test_model_string_representation(self):
        self.assertEqual(str(self.language), "Python")

    def test_create_language_with_same_name(self):
        with self.assertRaises(IntegrityError):
            ProgrammingLanguage.objects.create(name="Python")

    def test_name_cannot_be_blank(self):
        self.language.name = ''
        
        with self.assertRaises(ValidationError):
            self.language.full_clean() 
            self.language.save()
        