from django.test import TestCase
from expenses_tracker.form_models import BudgetForm


class BudgetFormTests(TestCase):
    def test_form_valid(self):
        # Create form data
        form_data = {
            'category': 'Groceries',
            'amount': '500.00',
            'description': 'Monthly groceries budget',
            'duration': '1 month',
        }

        # Instantiate the form with form data
        form = BudgetForm(data=form_data)

        # Check if the form is valid
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        # Create form data with missing required fields
        form_data = {
            'amount': '500.00',
            'description': 'Monthly groceries budget',
        }

        # Instantiate the form with incomplete form data
        form = BudgetForm(data=form_data)

        # Check if the form is invalid
        self.assertFalse(form.is_valid())

        # Check if the expected error messages are present in form errors
        self.assertIn('category', form.errors)
        self.assertIn('duration', form.errors)
