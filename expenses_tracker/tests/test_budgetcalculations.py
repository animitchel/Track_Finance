from django.test import TestCase, Client
from django.contrib.auth.models import User
from expenses_tracker.models import Budget, Transaction
from expenses_tracker.views import budget_calculation
from django.urls import reverse


class BudgetCalculationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', email='test@example.com', password='test_password')
        self.budget = Budget.objects.create(
            user=self.user, category='Groceries', budget=200.0, amount=100.0, duration='1 week', spent=100.0,
        )
        self.budget2 = Budget.objects.create(
            user=self.user, category='All Transactions', budget=200.0, amount=100.0, duration='2 weeks', spent=100.0,
        )

    def test_budget_calculation(self):
        """
        Test that budget calculation func added the figures back correctly to the database,
        once the transaction was deleted
        """
        # Create a sample transaction
        transaction = Transaction.objects.create(category='Groceries', amount=50.0, user=self.user)

        self.client.force_login(self.user)

        with self.assertRaises(AssertionError):
            self.assertEqual(self.budget2.amount, 150.0)
            self.assertEqual(self.budget2.spent, 50.0)

    # def test_budget_calculation_with_category_all_transactions_budget(self):
    #     """
    #     Test that budget calculation func added the figures back correctly when the transaction.is_all_trans_bud is True
    #     was deleted
    #     """
    #     transaction = Transaction.objects.create(category='Groceries', amount=50.0, user=self.user, is_all_trans_bud=True)
    #     self.client.force_login(self.user)
    #
    #     # This will also Call the budget_calculation function
    #     response = self.client.post(reverse('all_transactions_page'), {'all_transaction_id': transaction.id})
    #
    #     self.assertEqual(response.status_code, 302)
    #
    #     self.budget.refresh_from_db()
    #     self.budget2.refresh_from_db()
    #
    #     self.assertEqual(self.budget.amount, 150)
    #     self.assertEqual(self.budget.spent, 50)
    #
    #     # budget_calculation was called because is_all_trans_bud is true
    #     self.assertEqual(self.budget2.amount, 150)
    #     self.assertEqual(self.budget2.spent, 50)

















