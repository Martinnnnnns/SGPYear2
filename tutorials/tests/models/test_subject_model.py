from django.test import TestCase
from tutorials.models import Subject, ProgrammingLanguage

class SubjectTestCase(TestCase):
    def setUp(self):
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Flask", language=self.language, description="Web development in Flask")

    def test_subject_creation(self):
        self.assertEqual(self.subject.name, "Flask")
        self.assertEqual(self.subject.language.name, "Python")
        self.assertEqual(self.subject.description, "Web development in Flask")

    def test_subject_str_representation(self):
        self.assertEqual(str(self.subject), "Python - Flask - Web development in Flask")

    def test_subject_without_description(self):
        subject_without_desc = Subject.objects.create(name="Django", language=self.language)
        self.assertEqual(str(subject_without_desc), "Python - Django - No description")
