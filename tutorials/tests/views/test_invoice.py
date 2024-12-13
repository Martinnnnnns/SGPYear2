from io import BytesIO
from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import Invoice, Lesson, ProgrammingLanguage, Subject
from tutorials.views import InvoicePDFView
from django.utils.timezone import now
from PyPDF2 import PdfReader  # Add this import


User = get_user_model()

class InvoiceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password123",
            email="testuser@example.com",
        )
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Intro to Python", language=self.language)
        
        self.invoice = Invoice.objects.create(
            student=self.user,
            amount=100.50,
            status="unpaid",
            date=now(),
        )

        self.lesson = Lesson.objects.create(
            student=self.user,
            tutor=self.user,  # Dummy tutor
            lesson_datetime=now(),
            language=self.language,
            subject=self.subject,
            status="scheduled",
            invoice=self.invoice,
        )

    def test_create_invoice(self):
        self.assertEqual(self.invoice.student.username, "testuser")
        self.assertEqual(self.invoice.amount, 100.50)
        self.assertEqual(self.invoice.status, "unpaid")

    def test_invoice_str(self):
        self.assertEqual(
            str(self.invoice),
            f"Invoice {self.invoice.id} for {self.user.username} - {self.invoice.status}"
        )
    def test_student_invoices_view(self):
        """Test that student invoices are displayed correctly."""
        self.client.login(username="studentuser", password="password123")
        response = self.client.get(self.invoices_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_invoices.html")
        self.assertContains(response, f"Invoice #{self.invoice1.id}")
        self.assertContains(response, f"${self.invoice1.amount:.2f}")
        self.assertContains(response, f"Invoice #{self.invoice2.id}")
        self.assertContains(response, f"${self.invoice2.amount:.2f}")
        
    def test_generate_invoice_pdf(self):
        buffer = BytesIO()
        view = InvoicePDFView()
        view.generate_invoice_pdf(buffer, self.invoice)
        buffer.seek(0)  # Move to the beginning of the buffer
        reader = PdfReader(buffer)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()
        self.assertIn(f"Invoice #{self.invoice.id}", pdf_text)
        self.assertIn(f"${self.invoice.amount:.2f}", pdf_text)
        buffer.close()
