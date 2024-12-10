from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import Invoice

User = get_user_model()

class InvoiceModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )

    def test_create_invoice(self):
        # Create an invoice instance
        invoice = Invoice.objects.create(
            student=self.user,
            amount=100.50,
            status="unpaid"
        )
        # Test the invoice creation
        self.assertEqual(invoice.student.username, "testuser")
        self.assertEqual(invoice.amount, 100.50)
        self.assertEqual(invoice.status, "unpaid")

    def test_invoice_str(self):
        # Create an invoice instance
        invoice = Invoice.objects.create(
            student=self.user,
            amount=200.75,
            status="paid"
        )
        # Test the string representation
        self.assertEqual(
            str(invoice),
            f"Invoice {invoice.id} for {self.user.username} - {invoice.status}"
        )