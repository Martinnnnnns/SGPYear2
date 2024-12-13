from io import BytesIO
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from tutorials.models import Invoice, Lesson, ProgrammingLanguage, Subject
from tutorials.constants import UserRoles
from tutorials.views import InvoicePDFView
from django.utils.timezone import now
from PyPDF2 import PdfReader
from tutorials.tests.base import RoleSetupTest

User = get_user_model()

class InvoiceModelTest(RoleSetupTest):
    
    def setUp(self):
        # Create users with roles
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password=self.PASSWORD,
            email="admin@example.com",
        )
        self.admin_user.roles.add(self.admin_role)
        self.admin_user.current_active_role = self.admin_role
        self.admin_user.save()

        self.student_user = User.objects.create_user(
            username="student_user",
            password=self.PASSWORD,
            email="student@example.com",
        )
        self.student_user.roles.add(self.student_role)
        self.student_user.current_active_role = self.student_role
        self.student_user.save()

        self.tutor_user = User.objects.create_user(
            username="tutor_user",
            password=self.PASSWORD,
            email="tutor@example.com",
        )
        self.tutor_user.roles.add(self.tutor_role)
        self.tutor_user.current_active_role = self.tutor_role
        self.tutor_user.save()

        # Set up related models
        self.language = ProgrammingLanguage.objects.create(name="Python")
        self.subject = Subject.objects.create(name="Intro to Python", language=self.language)

        self.invoice = Invoice.objects.create(
            student=self.student_user,
            amount=100.50,
            status="unpaid",
            date=now(),
        )

        self.lesson = Lesson.objects.create(
            student=self.student_user,
            tutor=self.tutor_user,
            lesson_datetime=now(),
            language=self.language,
            subject=self.subject,
            status="scheduled",
            invoice=self.invoice,
        )

        self.invoice_url = reverse("invoice_pdf", args=[self.invoice.id])

    def test_create_invoice(self):
        """Test creating an invoice."""
        self.assertEqual(self.invoice.student.username, "student_user")
        self.assertEqual(self.invoice.amount, 100.50)
        self.assertEqual(self.invoice.status, "unpaid")

    def test_invoice_str(self):
        """Test the string representation of the invoice."""
        self.assertEqual(
            str(self.invoice),
            f"Invoice {self.invoice.id} for {self.student_user.username} - {self.invoice.status}",
        )

    def test_generate_invoice_pdf(self):
        """Test PDF generation for the invoice."""
        buffer = BytesIO()
        view = InvoicePDFView()
        view.generate_invoice_pdf(buffer, self.invoice)
        buffer.seek(0)
        reader = PdfReader(buffer)
        pdf_text = "".join([page.extract_text() for page in reader.pages])

        self.assertIn(f"Invoice #{self.invoice.id}", pdf_text)
        self.assertIn(f"${self.invoice.amount:.2f}", pdf_text)
        buffer.close()

    def test_student_can_access_own_invoice(self):
        """Test that a student can access their own invoice."""
        self.client.login(username="student_user", password=self.PASSWORD)
        response = self.client.get(self.invoice_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_student_cannot_access_other_invoice(self):
        """Test that a student cannot access someone else's invoice."""
        another_student = User.objects.create_user(
            username="other_student",
            password=self.PASSWORD,
            email="other_student@example.com"
        )
        another_student.roles.add(self.student_role)
        another_student.current_active_role = self.student_role
        another_student.save()

        self.client.login(username="other_student", password=self.PASSWORD)
        response = self.client.get(self.invoice_url)

        self.assertEqual(response.status_code, 403)
        self.assertIn("Unauthorized", response.content.decode())

    def test_admin_can_access_any_invoice(self):
        """Test that an admin can access any invoice."""
        self.client.login(username="admin_user", password=self.PASSWORD)
        response = self.client.get(self.invoice_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_invoice_not_found(self):
        """Test that accessing a non-existent invoice returns 404."""
        self.client.login(username="student_user", password=self.PASSWORD)
        non_existent_url = reverse("invoice_pdf", args=[999])
        response = self.client.get(non_existent_url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Invoice not found", response.content.decode())