from tutorials.models import Invoice
from tutorials.tests.base import RoleSetupTest
from tutorials.tests.mixins import StudentMixin

class InvoiceModelTest(RoleSetupTest, StudentMixin):
    def setUp(self):
        self.setup_student()
        self.invoice = Invoice.objects.create(
            student=self.student_user,
            amount=100.50,
            status='paid'
        )

    def test_invoice_str_method(self):
        #Expected string representation
        expected_str = f"Invoice {self.invoice.id} for {self.student_user.username} - {self.invoice.status}"
        self.assertEqual(str(self.invoice), expected_str)
