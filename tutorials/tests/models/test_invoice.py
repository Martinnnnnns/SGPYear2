from django.test import TestCase
from tutorials.models import Invoice, User

class InvoiceModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='testuser@example.com',
            first_name='John',
            last_name='Doe'
        )
        # Create a test invoice
        self.invoice = Invoice.objects.create(
            student=self.user,
            amount=100.50,
            status='paid'
        )

    def test_invoice_str_method(self):
        # Expected string representation
        expected_str = f"Invoice {self.invoice.id} for {self.user.username} - {self.invoice.status}"
        self.assertEqual(str(self.invoice), expected_str)
