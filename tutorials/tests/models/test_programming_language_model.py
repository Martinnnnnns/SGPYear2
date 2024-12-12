from django.test import TestCase
from tutorials.models import ProgrammingLanguage

from django.db import IntegrityError
from django.core.exceptions import ValidationError

class ProgrammingLanguageTestCase(TestCase):
    def setUp(self):
        """Setup code for test database."""
        self.language = ProgrammingLanguage.objects.create(name="Python")

    def test_model_string_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.language), "Python")

    def test_create_language_with_same_name(self):
        """Try to add language with the same name to DB."""
        with self.assertRaises(IntegrityError):
            ProgrammingLanguage.objects.create(name="Python")

    def test_name_cannot_be_blank(self):
        """Ensure name field cannot be blank"""
        self.language.name = ''
        
        with self.assertRaises(ValidationError):
            self.language.full_clean() 
            self.language.save()
        