from django.test import TestCase
from expenses_tracker.form_models import ExpenseIncomeReportForm  # Replace 'yourapp' with your app name


class TestExpenseIncomeReportForm(TestCase):
    def test_form_valid(self):
        # Define test data
        form_data = {
            'purpose': 'Test report',
            'note': 'This is a test report for unit testing.',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
        }

        # Create form instance with test data
        form = ExpenseIncomeReportForm(data=form_data)

        # Test form validation
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        # Define invalid test data (missing required fields)
        form_data = {}

        # Create form instance with invalid test data
        form = ExpenseIncomeReportForm(data=form_data)

        # Test form validation
        self.assertFalse(form.is_valid())

        # Test error messages
        self.assertIn('purpose', form.errors)
        self.assertIn('note', form.errors)
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)
