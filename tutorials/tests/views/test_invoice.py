from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import Invoice

User = get_user_model()

class InvoiceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )

    def test_create_invoice(self):
        invoice = Invoice.objects.create(
            student=self.user,
            amount=100.50,
            status="unpaid"
        )

        self.assertEqual(invoice.student.username, "testuser")
        self.assertEqual(invoice.amount, 100.50)
        self.assertEqual(invoice.status, "unpaid")

    def test_invoice_str(self):
        invoice = Invoice.objects.create(
            student=self.user,
            amount=200.75,
            status="paid"
        )

        self.assertEqual(
            str(invoice),
            f"Invoice {invoice.id} for {self.user.username} - {invoice.status}"
        )