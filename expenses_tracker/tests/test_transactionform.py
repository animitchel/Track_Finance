from django.test import TestCase
from expenses_tracker.form_models import TransactionForm


class TransactionFormTests(TestCase):
    def test_form_valid(self):
        # Create form data
        form_data = {
            'category': 'Groceries',
            'amount': '50.00',
            'description': 'Monthly groceries expense',
            'recurring_transaction': True,
            'frequency': 'monthly',
            'transaction_title': 'Groceries',
        }

        # Instantiate the form with form data
        form = TransactionForm(data=form_data)

        # Check if the form is valid
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        # Create form data with missing required fields
        form_data = {
            'amount': '50.00',
            'description': 'Monthly groceries expense',
        }

        # Instantiate the form with incomplete form data
        form = TransactionForm(data=form_data)

        # Check if the form is invalid
        self.assertFalse(form.is_valid())

        # Check if the expected error messages are present in form errors
        self.assertIn('category', form.errors)