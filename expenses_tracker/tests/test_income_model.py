from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from expenses_tracker.models import Income
from django.contrib.auth.models import User


class IncomeModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user for testing
        cls.user = User.objects.create(username='testuser')

    def test_model_fields(self):
        # Create an income instance
        income = Income.objects.create(
            category='salary or wages',
            amount=5000.0,
            notes='Monthly salary',
            date=timezone.now(),
            recurring_transaction=True,
            frequency='monthly',
            transaction_title='Salary',
            next_occurrence=timezone.now() + timedelta(weeks=4.4286),
            user=self.user
        )

        # Test fields
        self.assertEqual(income.category, 'salary or wages')
        self.assertEqual(income.amount, 5000.0)
        self.assertEqual(income.notes, 'Monthly salary')
        self.assertTrue(income.recurring_transaction)
        self.assertEqual(income.frequency, 'monthly')
        self.assertEqual(income.transaction_title, 'Salary')
        delta = timedelta(seconds=1)
        self.assertAlmostEqual(income.next_occurrence, timezone.now() + timedelta(weeks=4.4286), delta=delta)
        self.assertEqual(income.user, self.user)

    def test_save_method(self):
        # Create an income instance
        income = Income.objects.create(
            category='salary or wages',
            amount=5000.0,
            notes='Monthly salary',
            date=timezone.now(),
            recurring_transaction=True,
            frequency='monthly',
            user=self.user
        )

        # Test if next occurrence and transaction title are set correctly after saving
        expected_next_occurrence = timezone.now() + timedelta(weeks=4.4286)
        # self.assertEqual(income.next_occurrence, expected_next_occurrence)
        delta = timedelta(seconds=1)  # Adjust the delta as needed
        self.assertAlmostEqual(income.next_occurrence, expected_next_occurrence, delta=delta)
        self.assertEqual(income.transaction_title, 'salary or wages')

    def test_save_method_non_recurring(self):
        # Create a non-recurring income instance
        income = Income.objects.create(
            category='salary or wages',
            amount=5000.0,
            notes='One-time salary',
            date=timezone.now(),
            recurring_transaction=False,
            user=self.user
        )

        # Test if frequency and transaction title are reset to None after saving
        self.assertIsNone(income.frequency)
        self.assertIsNone(income.transaction_title)

    def test_string_representation(self):
        # Create an income instance
        income = Income(
            category='salary or wages',
            amount=5000.0,
            notes='Monthly salary',
            user=self.user
        )

        # Test string representation
        self.assertEqual(str(income), 'salary or wages - 5000.0')
