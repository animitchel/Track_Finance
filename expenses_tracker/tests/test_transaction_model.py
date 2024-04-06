from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from expenses_tracker.models import Transaction
from django.contrib.auth.models import User


class TransactionModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user for testing
        cls.user = User.objects.create(username='testuser')

    def test_model_fields(self):
        # Create a transaction instance
        transaction = Transaction.objects.create(
            category='Groceries',
            amount=100.0,
            description='Grocery shopping',
            recurring_transaction=True,
            frequency='monthly',
            transaction_title='Groceries',
            user=self.user
        )

        # Test fields
        self.assertEqual(transaction.category, 'Groceries')
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.description, 'Grocery shopping')
        self.assertTrue(transaction.recurring_transaction)
        self.assertEqual(transaction.frequency, 'monthly')
        self.assertEqual(transaction.transaction_title, 'Groceries')
        self.assertEqual(transaction.user, self.user)

    def test_next_occurrence(self):
        # Create a non-recurring transaction instance
        non_recurring_transaction = Transaction.objects.create(
            category='Groceries',
            amount=100.0,
            description='Grocery shopping',
            user=self.user
        )
        self.assertIsNone(non_recurring_transaction.next_occurrence)

        # Create a recurring transaction instance
        recurring_transaction = Transaction.objects.create(
            category='Groceries',
            amount=100.0,
            description='Monthly grocery shopping',
            recurring_transaction=True,
            frequency='monthly',
            user=self.user
        )

        # Test if next occurrence is set correctly
        expected_next_occurrence = timezone.now() + timedelta(weeks=4.4286)
        self.assertAlmostEqual(recurring_transaction.next_occurrence, expected_next_occurrence,
                               delta=timedelta(seconds=1))

    def test_transaction_title(self):
        # Create a recurring transaction without transaction title
        recurring_transaction = Transaction.objects.create(
            category='Groceries',
            amount=100.0,
            description='Monthly grocery shopping',
            recurring_transaction=True,
            frequency='monthly',
            user=self.user
        )

        # Test if transaction title is automatically set
        self.assertEqual(recurring_transaction.transaction_title, 'Groceries')

    def test_save_method(self):
        # Create a recurring transaction without transaction title
        recurring_transaction = Transaction(
            category='Groceries',
            amount=100.0,
            description='Monthly grocery shopping',
            recurring_transaction=True,
            frequency='monthly',
            user=self.user
        )

        # Save the transaction
        recurring_transaction.save()

        # Test if next occurrence and transaction title are set correctly after saving
        expected_next_occurrence = timezone.now() + timedelta(weeks=4.4286)
        self.assertAlmostEqual(recurring_transaction.next_occurrence, expected_next_occurrence,
                               delta=timedelta(seconds=1))
        self.assertEqual(recurring_transaction.transaction_title, 'Groceries')

    def test_string_representation(self):
        # Create a transaction instance
        transaction = Transaction(
            category='Groceries',
            amount=100.0,
            description='Grocery shopping',
            user=self.user
        )

        # Test string representation
        self.assertEqual(str(transaction), 'Groceries - 100.0')
