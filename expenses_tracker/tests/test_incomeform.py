from django.test import TestCase
from expenses_tracker.form_models import IncomeForm
from django.contrib.auth.models import User


class IncomeFormTests(TestCase):

    def test_form_valid(self):
        # Create form data
        form_data = {
            'category': 'salary or wages',
            'amount': '5000.00',
            'notes': 'Monthly salary',
            'frequency': 'monthly',
            'transaction_title': 'Salary',
            'recurring_transaction': True,
        }

        # Instantiate the form with form data
        form = IncomeForm(data=form_data)

        # Check if the form is valid
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        # Create form data with missing required fields
        form_data = {
            'category': 'Salary',
            'amount': '5000.00',
            'frequency': 'monthly',
        }

        # Instantiate the form with incomplete form data
        form = IncomeForm(data=form_data)

        # Check if the form is invalid
        self.assertFalse(form.is_valid())

        # Check if the expected error messages are present in form errors
        self.assertIn('notes', form.errors)
