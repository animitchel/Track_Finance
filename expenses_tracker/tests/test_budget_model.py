from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from expenses_tracker.models import Budget
from django.contrib.auth.models import User


class BudgetModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user for testing
        cls.user = User.objects.create(username='testuser')

    def test_model_fields(self):
        # Create a budget instance
        budget = Budget.objects.create(
            category='Groceries',
            amount=500.0,
            budget=1000.0,
            spent=300.0,
            description='Monthly grocery budget',
            duration='1 month',
            expiration_date=timezone.now() + timedelta(weeks=4.4286),
            user=self.user
        )

        # Test fields
        self.assertEqual(budget.category, 'Groceries')
        self.assertEqual(budget.amount, 500.0)
        self.assertEqual(budget.budget, 1000.0)
        self.assertEqual(budget.spent, 300.0)
        self.assertEqual(budget.description, 'Monthly grocery budget')
        self.assertEqual(budget.duration, '1 month')
        self.assertAlmostEqual(budget.expiration_date, timezone.now() + timedelta(weeks=4.4286), delta=timedelta(seconds=1))
        self.assertEqual(budget.user, self.user)

    def test_save_method(self):
        # Create a budget instance with spent as 0.0
        budget = Budget.objects.create(
            category='Groceries',
            amount=500.0,
            description='Monthly grocery budget',
            duration='1 month',
            user=self.user
        )

        # Test if expiration date is set correctly after saving
        expected_expiration_date = timezone.now() + timedelta(weeks=4.4286)
        self.assertAlmostEqual(budget.expiration_date, expected_expiration_date, delta=timedelta(seconds=1))

        # Create a budget instance with spent greater than 0.0
        budget_with_spent = Budget.objects.create(
            category='Groceries',
            amount=500.0,
            spent=300.0,
            description='Monthly grocery budget with spending',
            duration='1 month',
            user=self.user
        )

        # Test if expiration date is not set when spent is greater than 0.0
        self.assertIsNone(budget_with_spent.expiration_date)

    def test_string_representation(self):
        # Create a budget instance
        budget = Budget(
            category='Groceries',
            amount=500.0,
            description='Monthly grocery budget',
            user=self.user
        )

        # Test string representation
        self.assertEqual(str(budget), 'Groceries - 500.0')
