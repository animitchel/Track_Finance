from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from expenses_tracker.models import Transaction, Budget
from datetime import datetime


class TestDeleteTransactionView(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_delete_transaction(self):
        # Log in the test user
        self.client.login(username='testuser', password='password')

        # Create a transaction for testing
        transaction = Transaction.objects.create(
            user=self.user,
            amount=50.0,
            category='Test Category',
            is_all_trans_bud=True  # Set to True to test the case when it's True
        )

        # Create budget objects for testing
        budget_category = Budget.objects.create(
            user=self.user,
            category='Test Category',
            budget=100.0,
            amount=100.0,
            spent=0.0,
            duration="1 week"
        )

        all_transactions_budget = Budget.objects.create(
            user=self.user,
            category='All Transactions',
            budget=1000.0,
            amount=1000.0,
            spent=0.0,
            duration="2 weeks"
        )

        # Make a POST request to delete the transaction
        response = self.client.post(reverse('transaction_delete', kwargs={'pk': transaction.pk}))

        # Check that the transaction is deleted
        self.assertFalse(Transaction.objects.filter(id=transaction.id).exists())

        # Check that the budgets are recalculated correctly
        updated_budget_category = Budget.objects.get(id=budget_category.id)
        updated_all_transactions_budget = Budget.objects.get(id=all_transactions_budget.id)

        self.assertEqual(updated_budget_category.amount, 100.0)  # Budget increased by 50.0
        self.assertEqual(updated_budget_category.spent, 0.0)  # Spent amount decreased by 50.0

        self.assertEqual(updated_all_transactions_budget.amount, 1000.0)  # No change in budget
        self.assertEqual(updated_all_transactions_budget.spent, 0.0)  # No change in spent amount

        # Check that the view redirects to the correct URL after deletion
        self.assertRedirects(response, reverse('all_transactions_page'))
